# import the necessary libraries
#output.py
from huggingface_hub import hf_hub_download
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import numpy as np
import os
from Foodimg2Ing.args import get_parser
import pickle
from Foodimg2Ing.model import get_model
from torchvision import transforms
from utils.output_utils import prepare_output
from PIL import Image
import time
from tensorflow.keras.preprocessing import image
from Foodimg2Ing import app
from Foodimg2Ing import routes

def get_model_path(data_dir):
    """Helper function to get model path with proper error handling"""
    try:
        # First try to download from Hugging Face
        model_path = hf_hub_download(
            repo_id="dark-side/ai-recipe-generator-model",
            filename="modelbest.ckpt",
            cache_dir=data_dir
        )
        print(f"Successfully downloaded model from Hugging Face to {model_path}")
        return model_path
    except Exception as e:
        print(f"Error downloading model from Hugging Face: {e}")
        
        # Fallback to local path
        local_path = os.path.join(data_dir, 'modelbest.ckpt')
        if os.path.exists(local_path):
            print(f"Using locally cached model at {local_path}")
            return local_path
        else:
            raise RuntimeError("Model not found either on Hugging Face or locally")

def output(uploadedfile):
    """Process the image and return recipe information"""
    # Keep all the codes and pre-trained weights in data directory
    data_dir = './data'
    os.makedirs(data_dir, exist_ok=True)  # Ensure data directory exists

    # code will run in gpu if available and if the flag is set to True, else it will run on cpu
    use_gpu = True
    device = torch.device('cuda' if torch.cuda.is_available() and use_gpu else 'cpu')
    map_loc = None if torch.cuda.is_available() and use_gpu else 'cpu'

    try:
        # Load vocabulary files
        ingrs_vocab = pickle.load(open(os.path.join(data_dir, 'ingr_vocab.pkl'), 'rb'))
        vocab = pickle.load(open(os.path.join(data_dir, 'instr_vocab.pkl'), 'rb'))

        ingr_vocab_size = len(ingrs_vocab)
        instrs_vocab_size = len(vocab)
        output_dim = instrs_vocab_size

        # Initialize model
        import sys; sys.argv=['']; del sys
        args = get_parser()
        args.maxseqlen = 15
        args.ingrs_only = False
        model = get_model(args, ingr_vocab_size, instrs_vocab_size)
   
        # Load model
        model_path = get_model_path(data_dir)
        model.load_state_dict(torch.load(model_path, map_location=map_loc))
        model.to(device)
        model.eval()
        model.ingrs_only = False
        model.recipe_only = False

        # Prepare image transformations
        transf_list_batch = []
        transf_list_batch.append(transforms.ToTensor())
        transf_list_batch.append(transforms.Normalize((0.485, 0.456, 0.406), 
                                                    (0.229, 0.224, 0.225)))
        to_input_transf = transforms.Compose(transf_list_batch)

        # Load and transform image
        img = image.load_img(uploadedfile)
        transf_list = []
        transf_list.append(transforms.Resize(256))
        transf_list.append(transforms.CenterCrop(224))
        transform = transforms.Compose(transf_list)
        
        image_transf = transform(img)
        image_tensor = to_input_transf(image_transf).unsqueeze(0).to(device)

        # Generate recipe
        greedy = [True, False][0]  # Use only first option
        beam = [-1, -1][0]  # Use only first option
        temperature = 1.0

        with torch.no_grad():
            outputs = model.sample(image_tensor, greedy=greedy, 
                                temperature=temperature, beam=beam, true_ingrs=None)
                
        ingr_ids = outputs['ingr_ids'].cpu().numpy()
        recipe_ids = outputs['recipe_ids'].cpu().numpy()
                
        outs, valid = prepare_output(recipe_ids[0], ingr_ids[0], ingrs_vocab, vocab)
            
        if valid['is_valid']:
            return outs['title'], outs['ingrs'], outs['recipe']
        else:
            return "Not a valid recipe!", [], ["Reason: " + valid['reason']]

    except Exception as e:
        print(f"Error in output function: {str(e)}")
        return None, None, None

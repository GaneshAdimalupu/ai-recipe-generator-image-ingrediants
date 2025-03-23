"""Recipe page styles"""

def apply_recipe_styles():
    """Apply recipe page styles"""
    return """
    <style>
        /* Base Variables */
        :root {
            --primary-color: #FF4B4B;
            --primary-hover: #ff6b6b;
            --bg-color: #ffffff;
            --card-bg: #ffffff;
            --text-color: #1a1a1b;
            --text-secondary: #666;
            --border-color: #e6e6e6;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
            --transition-speed: 0.3s;
            --primary-color-rgb: 255, 75, 75;
            --light-purple: #E6E6FA;  

        }

        .page-title {
            color: var(--primary-color);
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }

        .page-subtitle {
            text-align: center;
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }

        .view-selector {
            background-color: var(--bg-color);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
        }

        .search-bar {
            margin: 1.5rem 0;
        }

        .search-bar input {
            width: 100%;
            padding: 0.75rem 1rem;
            border-radius: 25px;
            border: 1px solid var(--border-color);
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .search-bar input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(var(--primary-color-rgb), 0.1);
        }

        /* Recipe Card Styles */
        .recipe-card {
            background-color: var(--light-purple);
            border-radius: 16px;
            padding: 24px;
            margin: 20px 0;
            box-shadow: var(--shadow-sm);
            transition: all var(--transition-speed) ease;
            animation: cardEntrance 0.5s ease-out;
            border: 1px solid var(--border-color);
            color: #000;

        }

        .recipe-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
        }

        .recipe-title {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .recipe-info {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }

        .info-tag {
            background-color: rgba(var(--primary-color-rgb), 0.1);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s ease;
            # color: #000;

        }

        .info-tag:hover {
            background-color: rgba(var(--primary-color-rgb), 0.2);
            transform: translateY(-2px);
        }

        /* Animations */
        @keyframes cardEntrance {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #1a1a1b;
                --card-bg: #262626;
                --text-color: #e6e6e6;
                --text-secondary: #b0b0b0;
                --border-color: #404040;
            }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .recipe-info {
                flex-direction: column;
                gap: 0.5rem;
            }

            .recipe-card {
                padding: 1rem;
            }

            .page-title {
                font-size: 2rem;
            }
        }
    </style>
    """
import yaml

def build_config(initial_stack=None, small_blind=None, ante=None):
    config = {
            "initial_stack": initial_stack,
            "small_blind": small_blind,
            "ante": ante,
            "ai_players": [
                { "name": "FIXME:your-ai-name", "path": "FIXME:your-setup-script-path" },
            ]
            }
    print(yaml.dump(config, default_flow_style=False))


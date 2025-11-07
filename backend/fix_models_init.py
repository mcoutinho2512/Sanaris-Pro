import os
import re

models_dir = "app/models"
imports = []
all_classes = []

for filename in sorted(os.listdir(models_dir)):
    if filename.endswith(".py") and filename not in ["__init__.py"]:
        filepath = os.path.join(models_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            # Encontrar todas as classes que herdam de Base
            classes = re.findall(r'^class (\w+)\(Base\):', content, re.MULTILINE)
            if classes:
                module_name = filename[:-3]
                imports.append(f"from app.models.{module_name} import {', '.join(classes)}")
                all_classes.extend(classes)

# Gerar novo __init__.py
init_content = "\n".join(imports) + "\n\n__all__ = [\n"
for cls in all_classes:
    init_content += f'    "{cls}",\n'
init_content += "]\n"

print(init_content)

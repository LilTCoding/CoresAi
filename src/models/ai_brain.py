import logging
from datetime import datetime
from typing import Dict, Any, List
from .server_manager import ServerManager
from .enhanced_ai import EnhancedAI

class AIBrain:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory = []  # Conversational and action memory
        self.server_manager = ServerManager()
        self.language_ai = EnhancedAI()
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        # Stub: In production, load docs, FAQs, best practices, etc.
        return {
            "minecraft": {
                "common_mods": ["EssentialsX", "WorldEdit", "LuckPerms"],
                "setup_tips": "Always accept the EULA and configure server.properties."
            },
            "fivem_qb": {
                "common_resources": ["qb-core", "qb-policejob", "qb-vehicleshop"],
                "setup_tips": "Install QBcore and configure server.cfg."
            },
            # ... add more for other games ...
        }

    def remember(self, entry: Dict[str, Any]):
        self.memory.append({"timestamp": datetime.now().isoformat(), **entry})

    def get_memory(self) -> List[Dict[str, Any]]:
        return self.memory

    def generate_blueprint(self, game: str, description: str) -> Dict[str, Any]:
        # Use the language model to parse the description and generate a plan
        prompt = f"User wants to set up a {game} server: {description}. What steps, mods/plugins, and configs are needed?"
        ai_response = self.language_ai.process_input(prompt)
        self.remember({"type": "blueprint_request", "game": game, "description": description, "ai_response": ai_response})
        # For now, combine AI response with knowledge base
        kb = self.knowledge_base.get(game, {})
        return {
            "game": game,
            "description": description,
            "ai_plan": ai_response.get("response", ""),
            "suggested_mods": kb.get("common_mods", []) or kb.get("common_resources", []),
            "setup_tips": kb.get("setup_tips", "")
        }

    def suggest_mods(self, game: str, description: str) -> List[str]:
        # Use AI and knowledge base to suggest mods/plugins/resources
        kb = self.knowledge_base.get(game, {})
        ai_suggestion = self.language_ai.process_input(f"Suggest mods/plugins for a {game} server: {description}")
        self.remember({"type": "mod_suggestion", "game": game, "description": description, "ai_response": ai_suggestion})
        return list(set(kb.get("common_mods", []) + kb.get("common_resources", []) + [ai_suggestion.get("response", "")]))

    def step_by_step_help(self, game: str, current_step: str, context: Dict[str, Any]) -> str:
        # Use AI to provide step-by-step guidance
        prompt = f"Help the user with this step for a {game} server: {current_step}. Context: {context}"
        ai_response = self.language_ai.process_input(prompt)
        self.remember({"type": "step_help", "game": game, "step": current_step, "context": context, "ai_response": ai_response})
        return ai_response.get("response", "")

    def handle_file_edit(self, game: str, filepath: str, edit_instruction: str) -> Dict[str, Any]:
        # Use AI to edit a file based on an instruction
        file_content = self.server_manager.read_file(game, filepath).get("content", "")
        prompt = f"Edit this file for a {game} server based on the instruction: {edit_instruction}\nFile content:\n{file_content}"
        ai_response = self.language_ai.process_input(prompt)
        new_content = ai_response.get("response", file_content)
        self.server_manager.write_file(game, filepath, new_content)
        self.remember({"type": "file_edit", "game": game, "filepath": filepath, "instruction": edit_instruction, "ai_response": ai_response})
        return {"status": "success", "new_content": new_content} 
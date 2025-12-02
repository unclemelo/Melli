from avatar import vmc_client


class DialogueManager:
    def build_prompt(self, author: str, message: str) -> str:
        return f"{author} says: {message}\nRespond as a friendly anime VTuber persona. Keep replies short and friendly."


    def detect_emotion(self, text: str) -> str:
        t = text.lower()
        if any(x in t for x in ["lol","haha","yay","nice","cool","love"]):
            return "happy"
        if any(x in t for x in ["sad","not good","unfortunate","sorry"]):
            return "sad"
        if any(x in t for x in ["angry","stupid","wtf","hate"]):
            return "angry"
        return "neutral"


    def apply_emotion(self, vmc, emotion: str):
        if emotion == "happy":
            vmc_client.Expressions.smile(vmc)
            vmc_client.Bones.nod_head(vmc)
        elif emotion == "angry":
            vmc_client.Expressions.angry(vmc)
        elif emotion == "sad":
            vmc_client.Expressions.sad(vmc)
        else:
            vmc_client.Expressions.neutral(vmc)
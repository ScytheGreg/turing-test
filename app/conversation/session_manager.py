from app.conversation.controller import ConversationController


class SessionManager:

  def __init__(self) -> None:
    # Słownik przechowujący osobne kontrolery dla Alice i Boba
    self._sessions: dict[str, ConversationController] = {
        "alice": ConversationController(),
        "bob": ConversationController(),
    }

  def get_controller(self, session_id: str) -> ConversationController:
    sid = session_id.lower()
    if sid not in self._sessions:
      raise ValueError(f"Nieznana sesja: {session_id}. Dostępne: alice, bob")
    return self._sessions[sid]


# Globalna instancja zarządcy
session_manager = SessionManager()

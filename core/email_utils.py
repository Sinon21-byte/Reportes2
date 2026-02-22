import logging
import threading

logger = logging.getLogger(__name__)

def send_email_async(message):
    def _send():
        try:
            message.send(fail_silently=False)
            logger.info("Reporte enviado por correo a %s.", ", ".join(message.to))
        except Exception:
            logger.exception(
                "Error al enviar el reporte por correo a %s.",
                ", ".join(message.to),
            )

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

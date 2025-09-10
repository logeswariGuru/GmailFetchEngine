import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def modify_message(service, email_id, add_labels=None, remove_labels=None):
    """Helper to modify Gmail message labels."""
    body = {}
    if add_labels:
        body["addLabelIds"] = add_labels
    if remove_labels:
        body["removeLabelIds"] = remove_labels

    service.users().messages().modify(
        userId="me",
        id=email_id,
        body=body
    ).execute()


def apply_actions(service, email, actions):
    """Apply Gmail actions (mark read/unread, move)."""
    email_id = email.get("id")
    logger.info("apply_actions-----> %s", email_id)

    for action in actions:
        try:
            atype = action.get("type")

            if atype == "mark_as_read":
                modify_message(service, email_id, remove_labels=["UNREAD"])
                logger.info("📩 Marked email %s as read", email_id)

            elif atype == "mark_as_unread":
                modify_message(service, email_id, add_labels=["UNREAD"])
                logger.info("📩 Marked email %s as unread", email_id)

            elif atype == "move":
                destination = action.get("destination")
                if not destination:
                    logger.warning("⚠️ No destination provided for move action.")
                    continue
                modify_message(service, email_id, add_labels=[destination], remove_labels=["INBOX"])
                logger.info("📂 Moved email %s to %s", email_id, destination)

            else:
                logger.warning("⚠️ Unsupported action type: %s", atype)

        except Exception as e:
            logger.error("❌ Failed to apply action %s on email %s: %s", action, email_id, e)

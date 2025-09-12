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
    logger.info(f"apply_actions → {email.get('id')}")

    email_id = email.get("id")
    is_read = email.get("is_read", 0)      # default to unread (0)
    labels = email.get("labels", [])        # default to empty list

    for action in actions:
        try:
            atype = action.get("type")

            if atype == "mark_as_read":
                # Always attempt to remove the UNREAD label in Gmail.
                modify_message(service, email_id, remove_labels=["UNREAD"]) 
                logger.info("📩 Marked email %s as read (requested)", email_id)

            elif atype == "mark_as_unread":
                # Always attempt to add the UNREAD label in Gmail.
                modify_message(service, email_id, add_labels=["UNREAD"]) 
                logger.info("📩 Marked email %s as unread (requested)", email_id)

            elif atype == "move":
                destination = action.get("destination")
                if not destination:
                    logger.warning("⚠️ No destination provided for move action.")
                    continue

                # Always attempt to add the destination label and remove INBOX.
                modify_message(service, email_id, add_labels=[destination], remove_labels=["INBOX"])
                logger.info("📂 Moved email %s to %s (requested)", email_id, destination)

            else:
                logger.warning("⚠️ Unsupported action type: %s", atype)

        except Exception as e:
            logger.error("❌ Failed to apply action %s on email %s: %s", action, email_id, e)

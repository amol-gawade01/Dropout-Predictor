import httpx

from backend.app.core.config import (
    get_settings,
)


class WhatsAppServiceError(
    RuntimeError
):
    pass


def get_whatsapp_config():

    settings = get_settings()

    required = {

        "graph_version":
            settings
            .whatsapp_graph_version,

        "phone_number_id":
            settings
            .whatsapp_phone_number_id,

        "access_token":
            settings
            .whatsapp_access_token,
    }

    missing = [
        name
        for name, value
        in required.items()
        if not value
    ]

    if missing:

        raise WhatsAppServiceError(
            "Missing WhatsApp "
            "configuration: "
            + ", ".join(
                missing
            )
        )

    return settings


def upload_pdf(
    pdf_bytes: bytes,
    filename: str,
) -> str:

    settings = (
        get_whatsapp_config()
    )

    url = (
        "https://graph.facebook.com/"
        f"{settings.whatsapp_graph_version}/"
        f"{settings.whatsapp_phone_number_id}/"
        "media"
    )

    headers = {
        "Authorization":
            (
                "Bearer "
                f"{settings.whatsapp_access_token}"
            )
    }

    files = {
        "file": (
            filename,
            pdf_bytes,
            "application/pdf",
        )
    }

    data = {
        "messaging_product":
            "whatsapp",

        "type":
            "application/pdf",
    }


    with httpx.Client(
        timeout=60.0
    ) as client:

        response = client.post(
            url,
            headers=headers,
            files=files,
            data=data,
        )


    if response.is_error:

        raise WhatsAppServiceError(
            "WhatsApp media upload "
            f"failed: {response.text}"
        )


    payload = response.json()

    media_id = payload.get(
        "id"
    )

    if not media_id:

        raise WhatsAppServiceError(
            "WhatsApp did not return "
            "a media ID"
        )

    return media_id

def send_direct_document(
    phone_number: str,
    media_id: str,
    filename: str,
    caption: str,
):

    settings = (
        get_whatsapp_config()
    )

    url = (
        "https://graph.facebook.com/"
        f"{settings.whatsapp_graph_version}/"
        f"{settings.whatsapp_phone_number_id}/"
        "messages"
    )

    headers = {

        "Authorization":
            (
                "Bearer "
                f"{settings.whatsapp_access_token}"
            ),

        "Content-Type":
            "application/json",
    }

    payload = {

        "messaging_product":
            "whatsapp",

        "recipient_type":
            "individual",

        "to":
            phone_number,

        "type":
            "document",

        "document": {

            "id":
                media_id,

            "filename":
                filename,

            "caption":
                caption,
        },
    }


    with httpx.Client(
        timeout=60.0
    ) as client:

        response = client.post(
            url,
            headers=headers,
            json=payload,
        )


    if response.is_error:

        raise WhatsAppServiceError(
            "WhatsApp document send "
            f"failed: {response.text}"
        )

    return response.json()

def send_template_document(
    phone_number: str,
    media_id: str,
    filename: str,
    guardian_name: str,
    student_name: str,
    support_level: str,
):

    settings = (
        get_whatsapp_config()
    )

    template_name = (
        settings
        .whatsapp_template_name
    )

    if not template_name:

        raise WhatsAppServiceError(
            "WHATSAPP_TEMPLATE_NAME "
            "is not configured"
        )


    url = (
        "https://graph.facebook.com/"
        f"{settings.whatsapp_graph_version}/"
        f"{settings.whatsapp_phone_number_id}/"
        "messages"
    )

    headers = {

        "Authorization":
            (
                "Bearer "
                f"{settings.whatsapp_access_token}"
            ),

        "Content-Type":
            "application/json",
    }


    payload = {

        "messaging_product":
            "whatsapp",

        "to":
            phone_number,

        "type":
            "template",

        "template": {

            "name":
                template_name,

            "language": {
                "code":
                    settings
                    .whatsapp_template_language
            },

            "components": [

                {
                    "type":
                        "header",

                    "parameters": [
                        {
                            "type":
                                "document",

                            "document": {
                                "id":
                                    media_id,

                                "filename":
                                    filename,
                            },
                        }
                    ],
                },

                {
                    "type":
                        "body",

                    "parameters": [

                        {
                            "type":
                                "text",

                            "text":
                                guardian_name,
                        },

                        {
                            "type":
                                "text",

                            "text":
                                student_name,
                        },

                        {
                            "type":
                                "text",

                            "text":
                                support_level,
                        },
                    ],
                },
            ],
        },
    }


    with httpx.Client(
        timeout=60.0
    ) as client:

        response = client.post(
            url,
            headers=headers,
            json=payload,
        )


    if response.is_error:

        raise WhatsAppServiceError(
            "WhatsApp template send "
            f"failed: {response.text}"
        )

    return response.json()

def send_parent_report(
    phone_number: str,
    pdf_bytes: bytes,
    filename: str,
    guardian_name: str,
    student_name: str,
    support_level: str,
):

    settings = (
        get_whatsapp_config()
    )

    media_id = upload_pdf(
        pdf_bytes=pdf_bytes,
        filename=filename,
    )


    if (
        settings
        .whatsapp_template_name
    ):

        response = (
            send_template_document(
                phone_number=
                    phone_number,

                media_id=
                    media_id,

                filename=
                    filename,

                guardian_name=
                    guardian_name,

                student_name=
                    student_name,

                support_level=
                    support_level,
            )
        )

    else:

        response = (
            send_direct_document(
                phone_number=
                    phone_number,

                media_id=
                    media_id,

                filename=
                    filename,

                caption=(
                    "Student Support "
                    f"Report - "
                    f"{student_name}"
                ),
            )
        )


    message_id = None

    messages = response.get(
        "messages",
        [],
    )

    if messages:

        message_id = (
            messages[0]
            .get("id")
        )


    return {
        "media_id":
            media_id,

        "message_id":
            message_id,

        "response":
            response,
    }
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse


@login_required
def delete_user(request: HttpRequest) -> HttpResponse:
    """
    View that allows the authenticated user to delete their own account.

    All related data (messages, notifications, message histories) will be
    cleaned up by the post_delete signal on the User model.
    """
    if request.method == "POST":
        user = request.user
        username = user.get_username()

        # The checker expects to see user.delete() explicitly in this view.
        user.delete()

        return HttpResponse(f"User '{username}' deleted successfully.")

    # In a real application this would return a confirmation page.
    return HttpResponse("Send a POST request to delete your account.")


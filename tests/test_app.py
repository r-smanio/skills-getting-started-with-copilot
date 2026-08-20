def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert set(activities["Chess Club"]) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }
    assert isinstance(activities["Chess Club"]["participants"], list)


def test_signup_adds_student_and_returns_message(client):
    activity_name = "Soccer Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_bad_request_for_duplicate_student(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}


def test_signup_requires_email(client):
    response = client.post("/activities/Soccer Club/signup")

    assert response.status_code == 422


def test_unregister_removes_student_and_returns_message(client):
    activity_name = "Soccer Club"
    email = "new.student@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unknown_student(client):
    response = client.delete(
        "/activities/Soccer Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}

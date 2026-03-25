from src.app import activities


def test_get_activities_returns_expected_shape(client):
    # Arrange
    expected_count = 9

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert len(payload) == expected_count

    sample = payload["Chess Club"]
    assert "description" in sample
    assert "schedule" in sample
    assert "max_participants" in sample
    assert "participants" in sample


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 302)
    assert response.headers["location"] == expected_location


def test_signup_success_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_signup_success_removes_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "james@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_delete_signup_for_non_enrolled_email_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.enrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_delete_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_missing_email_returns_422(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_delete_signup_missing_email_returns_422(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_url_encoded_activity_name_works_for_signup(client):
    # Arrange
    encoded_activity_name = "Chess%20Club"
    decoded_activity_name = "Chess Club"
    email = "encoded.path@mergington.edu"

    # Act
    response = client.post(f"/activities/{encoded_activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[decoded_activity_name]["participants"]


def test_signup_allows_over_max_participants_current_behavior(client):
    # Arrange
    activity_name = "Chess Club"
    max_participants = activities[activity_name]["max_participants"]

    for idx in range(max_participants):
        activities[activity_name]["participants"].append(f"seed{idx}@mergington.edu")

    over_limit_email = "overflow@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": over_limit_email})

    # Assert
    assert response.status_code == 200
    assert over_limit_email in activities[activity_name]["participants"]

from snake_eyes.blueprints.user.models import User


class TestUserModel:
    def test_serialize_token(self, token):
        """Test token serializer works correctly"""
        assert token.count(".") == 2

    def test_desrialize_token(self, token):
        """Test token deserializer works correctly"""
        user = User.deserialize_token(token)
        assert user.email == "admin@localhost"

    def test_desrialize_token_tampered(self, token):
        """Test token deserializer works correctly for tampered token"""
        user = User.deserialize_token(f"{token}xyz")
        assert user is None

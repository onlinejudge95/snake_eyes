from flask import url_for


class TestPage:
    def test_home_page(self, client):
        """
        Home page should return 200
        Title should exists in the html response
        """
        home_page_url = url_for("page.home")
        response = client.get(home_page_url)

        assert response.status_code == 200
        assert "<title>" in str(response.data)

    def test_privacy_page(self, client):
        """
        Privacy page should return 200
        Title should exists in the html response
        """
        privacy_page_url = url_for("page.privacy")
        response = client.get(privacy_page_url)

        assert response.status_code == 200
        assert "<title>" in str(response.data)

    def test_terms_page(self, client):
        """
        Terms page should return 200
        Title should exists in the html response
        """
        terms_page_url = url_for("page.terms")
        response = client.get(terms_page_url)

        assert response.status_code == 200
        assert "<title>" in str(response.data)

import unittest

from app import analyze_password, app


class PassSecureTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password Analyzer', response.data)

    def test_password_analysis(self):
        response = self.client.post('/', data={'password': 'StrongPass123!'} )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Excellent', response.data)

    def test_password_generation(self):
        response = self.client.post('/generate', data={'length': '16'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Generated Password', response.data)

    def test_repeated_password_is_not_strong(self):
        response = self.client.post('/', data={'password': '111111111111111111'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Weak', response.data)

    def test_strong_password_scores_maximum(self):
        analysis = analyze_password('Aa1!Bb2@Cc3#Dd4$')
        self.assertEqual(analysis['score'], 100)
        self.assertEqual(analysis['strength'], 'Excellent')


if __name__ == '__main__':
    unittest.main()

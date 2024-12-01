import requests


class Exercise:
    @staticmethod
    def get_exercise():
        base_api = "http://localhost:8080/api/v1/exercises"
        try:
            response = requests.get(base_api + "/random")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

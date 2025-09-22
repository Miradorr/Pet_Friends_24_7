import requests
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

class PetFriends:

    def __init__(self):
        self.base_url = "https://petfriends.skillfactory.ru/"

    def get_api_key(self, email: str, passwd: str) -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
        JSON с уникальным ключем пользователя, найденного по указанным email и паролем"""

        headers = {
            'email': email,
            'password': passwd,
        }
        res = requests.get(self.base_url+'api/key', headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def get_list_of_pets(self, auth_key: json, filter: str = "") -> json:
        """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате JSON
        со списком наденных питомцев, совпадающих с фильтром. На данный момент фильтр может иметь
        либо пустое значение - получить список всех питомцев, либо 'my_pets' - получить список
        собственных питомцев"""

        headers = {'auth_key': auth_key['key']}
        filter = {'filter': filter}

        res = requests.get(self.base_url + 'api/pets', headers=headers, params=filter)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_info_about_new_pet(self, auth_key: dict, name: str, animal_type: str, age: str, pet_photo: str) -> tuple:
        data = {'name': name, 'animal_type': animal_type, 'age': age}
        headers = {'auth_key': auth_key.get('key', '')}

        files = {}
        if pet_photo is not None and pet_photo != '':
            try:
                files['pet_photo'] = open(pet_photo, 'rb')
            except FileNotFoundError:
                raise

        if files:
            res = requests.post(self.base_url + '/add_pet', headers=headers, data=data, files=files)
            files['pet_photo'].close()
        else:
            res = requests.post(self.base_url + '/add_pet_no_photo', headers=headers, data=data)

        return res.status_code, res.json()

    def delete_pet(self, auth_key: json, pet_id: str) -> json:
        """Метод отправляет на сервер запрос на удаление питомца по указанному ID и возвращает
        статус запроса и результат в формате JSON с текстом уведомления о успешном удалении.
        На сегодняшний день тут есть баг - в result приходит пустая строка, но status при этом = 200"""

        headers = {'auth_key': auth_key['key']}

        res = requests.delete(self.base_url + 'api/pets/' + pet_id, headers=headers)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def update_pet_info(self, auth_key: json, pet_id: str, name: str,
                        animal_type: str, age: int) -> json:
        """Метод отправляет запрос на сервер о обновлении данных питомуа по указанному ID и
        возвращает статус запроса и result в формате JSON с обновлённыи данными питомца"""

        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'age': age,
            'animal_type': animal_type
        }

        res = requests.put(self.base_url + 'api/pets/' + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def add_info_about_new_pet(self, auth_key: dict, name: str, animal_type: str, age: str, pet_photo: str) -> tuple:

        data = {'name': name,'animal_type': animal_type, 'age': age}

        headers = {'auth_key': auth_key.get('key', '')}

        files = {'pet_photo': open(pet_photo, 'rb')}

        res = requests.post(self.base_url + 'api/pets/', headers=headers, data=data, files=files)
        status = res.status_code

        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result


    def add_photo_of_pets(self, auth_key: json, pet_id: str, pet_photo: str) -> tuple:

        headers = {'auth_key': auth_key['key']}

        files = {'pet_photo': open(pet_photo, 'rb')}

        res = requests.post(self.base_url + f'/ api/pets/set_photo/{pet_id}', headers=headers, files=files)
        status = res.status_code

        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result
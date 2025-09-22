import pytest
import os
from api import PetFriends
from settings import valid_email, valid_password

pf = PetFriends()


@pytest.fixture
def auth_key():
    """Фикстура для получения действующего auth_key"""
    status, result = pf.get_api_key(valid_email, valid_password)
    assert status == 200, f"Не удалось получить API ключ. Статус: {status}, ответ: {result}"
    assert 'key' in result, "В ответе отсутствует ключ авторизации"
    return result


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result # controllo se nel resultato torna la chiave


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)# _, non ci serve status - polucili key
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0 # pets come viene dato l'elenco dei animali


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_api_key_for_valid_user():
    """Проверяем, что запрос API ключа возвращает статус 200 и содержит ключ"""
    status, result = pf.get_api_key(valid_email, valid_password)
    assert status == 200, f"Ожидался статус 200, но получен {status}"
    assert 'key' in result, "Ключ авторизации отсутствует в ответе"


def test_get_api_key_with_invalid_user():
    """Проверяем, что при неверных данных ключ не возвращается"""
    status, result = pf.get_api_key("wrong@example.com", "wrongpassword")
    assert status == 403, f"Ожидался статус 403, но получен {status}"
    assert 'key' not in result, "Ключ не должен быть в ответе при неверных данных"


def test_get_all_pets_with_valid_key(auth_key):
    """Проверяем, что список всех питомцев не пустой"""
    status, result = pf.get_list_of_pets(auth_key, filter='')
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(auth_key):
    """Проверяем возможность добавления питомца с корректными данными"""
    pet_photo = os.path.join(os.path.dirname(__file__), 'images/cat1.jpg')
    status, result = pf.add_new_pet(auth_key, 'Барбоскин', 'двортерьер', '4', pet_photo)
    assert status == 200
    assert result['name'] == 'Барбоскин'


def test_successful_delete_self_pet(auth_key):
    """Проверяем возможность удаления своего питомца"""
    status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200

    if not my_pets['pets']:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", os.path.join(os.path.dirname(__file__), 'images/cat1.jpg'))
        status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        assert status == 200

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    assert status == 200

    status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200
    assert pet_id not in [pet['id'] for pet in my_pets['pets']]


def test_successful_update_self_pet_info(auth_key):
    """Проверяем возможность обновления информации о питомце"""
    status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 200

    if not my_pets['pets']:
        raise Exception("Нет питомцев для обновления")

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.update_pet_info(auth_key, pet_id, "Мурзик", "Котэ", 5)
    assert status == 200
    assert result['name'] == "Мурзик"


def test_add_pet_without_auth_key():
    """Проверка запрета на добавление питомца без авторизации"""
    pet_photo = os.path.join(os.path.dirname(__file__), 'images/cat1.jpg')
    status, result = pf.add_info_about_new_pet({}, 'Tom', 'cat', '3', pet_photo)

    assert status != 200, f"Питомец был добавлен без авторизации! Статус: {status}, ответ: {result}"

    if isinstance(result, dict):
        assert 'error' in result or 'message' in result, f"Нет ожидаемой ошибки. Ответ: {result}"
    else:
        assert "error" in result.lower() or "not found" in result.lower() or status in [401, 403], f"Неожиданный ответ: {result}"


def test_add_pet_with_empty_fields(auth_key):
    """Проверка запрета на добавление питомца с пустыми полями"""
    pet_photo = os.path.join(os.path.dirname(__file__), 'images/cat1.jpg')
    status, result = pf.add_info_about_new_pet(auth_key, '', '', '', pet_photo)
    assert status != 200
    assert 'error' in result or 'name' not in result


def test_add_pet_with_invalid_photo_path(auth_key):
    """Проверка, что нельзя добавить питомца с несуществующим фото"""
    invalid_path = os.path.join(os.path.dirname(__file__), 'images/does_not_exist.jpg')
    assert not os.path.exists(invalid_path), "Файл неожиданно существует"

    with pytest.raises(FileNotFoundError):
        pf.add_info_about_new_pet(auth_key, 'Фантом', 'кот', '5', invalid_path)



def test_get_my_pets_with_invalid_filter():
    """Проверяем получение питомцев с неверным фильтром"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, "неверный_фильтр")
    assert status == 500



def test_get_api_key_with_invalid_email():
    """Проверяем запрос API ключа с неверным email"""
    status, result = pf.get_api_key("invalid@email.com", valid_password)
    assert status == 403
    assert 'key' not in result

def test_get_api_key_with_invalid_password():
    """Проверяем запрос API ключа с неверным паролем"""
    status, result = pf.get_api_key(valid_email, "invalid_password")
    assert status == 403
    assert 'key' not in result


def test_get_all_pets_with_invalid_auth_key():
    """Проверка отказа при использовании недействительного auth_key"""
    invalid_key = {"key": "123invalidkey"}
    status, result = pf.get_list_of_pets(invalid_key, "")

    assert status in [403, 401], f"Ожидался отказ в доступе. Статус: {status}, ответ: {result}"
    assert 'error' in result or isinstance(result, str), "Ожидалось сообщение об ошибке"


def test_update_pet_with_invalid_id():
    """Проверяем обновление информации о несуществующем питомце"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.update_pet_info(auth_key, "999999", "НовоеИмя", "НовыйТип", "10")
    assert status == 400



class APClient:

    """ Методы Вконтакте"""

    Api_base_url = 'https://api.vk.com/method'
    def __init__(self, vk_token, user_id, ya_token):
        self.vk_token = vk_token
        self.user_id = user_id
        self.ya_token = ya_token

    def get_common_params(self):
        return {
            'access_token': self.vk_token,
            'v': '5.131'
        }

    def get_profile_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'wall', 'photo_sizes': 1, 'extended': 1})
        response = requests.get(
            f"{self.Api_base_url}/photos.get", params=params)
        return response.json()

    def max_size_photo(self, number): #number это порядковый номер фото в списке фоток
        max_height = 0
        user_photos = self.get_profile_photos()
        photo_size_list = user_photos.get('response', {}).get('items')[number].get('sizes')  # список размеров одной фотки
        photo_date = user_photos.get('response', {}).get('items')[number].get('date')
        likes_count = user_photos.get('response', {}).get('items')[number].get('likes').get('count')
        for photo in photo_size_list:
            if photo['height'] > max_height:
                max_height = photo['height']
                max_size_url = str(photo['url'])
                photo_type = photo['type']
        return max_size_url, photo_type, photo_date, likes_count

    def list_of_photos_to_upload(self):
        user_photos = self.get_profile_photos()
        photo_count = user_photos.get('response', {}).get('count')
        lst =[]
        for number in range(photo_count):
            lst.append(self.max_size_photo(number))
        return lst

    def unix_to_timestamp(self,value):
        from datetime import datetime
        value = datetime.fromtimestamp(value)
        return value.strftime('%Y_%m_%d %Hhr %Mmin')

    def Json_file(self):
        lst = self.list_of_photos_to_upload()
        photos_list = []
        file_name_list = []
        photo_id_dict ={}
        # pprint(lst)
        for item in lst: #присвоение имени (если лайки дублируются до берется дата, если дата уже есть, то добавляем photo ver
            # item [2] id файла
            likes_count = item[3]

            if likes_count in file_name_list:
                file_name = self.unix_to_timestamp(item[2])

                if item[2] in photo_id_dict.keys():
                    photo_id_dict[item[2]] += 1
                    file_name = f'{file_name} photo {photo_id_dict[item[2]]}'

                else:
                    photo_id_dict[item[2]] = 1
            else:
                file_name = likes_count
                file_name_list.append(file_name)
                photo_id_dict[item[2]] = 1
            photos_list.append({'file_name': f'{file_name}.jpeg', 'size': item[1]})
        with open('photos_logу.json', 'w') as file:
            json.dump(photos_list, file)

        return photos_list

    def files_save_in_python(self):
        lst = self.list_of_photos_to_upload()
        for item in tqdm(range(len(lst)), desc='VK files download'):
            photo_url = lst[item][0]
            file_name = self.Json_file()[item].get('file_name')
            response = requests.get(photo_url)
            with open(file_name, 'wb') as file:
                file.write(response.content)


    """Методы Яндекс"""

    ya_base_url = 'https://cloud-api.yandex.net'

    def ya_common_headers(self):
        return {'Authorization': f'OAuth {self.ya_token}'}

    def ya_folder(self, folder):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': folder
        }
        headers = self.ya_common_headers()
        requests.put(url, params=params, headers=headers)

    def ya_upload_link(self, folder, file_name):
        params = {'path': f'{folder}/{file_name}'}
        headers = self.ya_common_headers()
        response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                params=params, headers=headers).json()
        upload_link = response.get('href')
        return upload_link

    def ya_file_upload(self, folder):
        print("\033[32m {}".format('WARMING UP...'))
        self.ya_folder(folder)
        self.files_save_in_python()
        for item in tqdm(self.Json_file(), desc='YA files upload'):
            file_name = item['file_name']
            with open(file_name, 'rb') as file:
                response = requests.put(self.ya_upload_link(folder, file_name), files={'file': file})
            self.file_delete(file_name)
        print("\033[32m {}".format('COMPLETED!'))

    def file_delete(self,file): # удаление файла с компьютера после его закачки на яндекс
        os.remove(file)



if __name__ == '__main__':
    import requests
    from tqdm import tqdm
    import os
    import json
    from urllib.parse import urlencode
    from pprint import pprint

    user_id = int(input('INPUT USER ID VK'))
    vk_token = input('INPUT VK TOKEN')
    ya_token = input('INPUT YANDEX TOKEN')
    folder = input('INPUT FOLDER NAME')


    App_ID = '51750980'
    # user_id = 822203161  # мой ВК номер

    vk_client = APClient(vk_token, user_id, ya_token)

    vk_client.ya_file_upload(folder)  # активация программы с казанием имени папки на Yandex

    # vk_client.ya_upload_link()
    # pprint(vk_client.get_profile_photos())
    # print(vk_client.get_status())
    # print(vk_client.set_status('allhbn gud'))
    # print(vk_client.get_status())
    # pprint(vk_client.list_of_photos_to_upload())
    # print(vk_client.Json_file())
    # vk_client.files_save_in_python()
    # vk_client.max_size_photo(0)..








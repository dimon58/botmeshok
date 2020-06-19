class Music():
    class descriptions():
        join = 'Присоединяет к вашему голосовому каналу'
        leave = 'Отсоединяет от голосового канала'
        play = 'Проигрывает музыку с Youtube'
        pause = 'Ставит музыку на паузу'
        resume = 'Возобновляет музыку'
        stop = 'Останавливает музыку'
        skip = 'Пропускает песню в очереди'
        volume = 'Изменяет громкость (максимум=300)'
        queue = 'Показывает вашу очередь воспроизведения'
        dequeue = 'Удаляет песню из очереди'
        clearqueue = 'Очищает очередь воспроизведения'
        loop = 'Переключает между циклированием всех, одного или выключает его'
        playlist = 'Доступ к функциям плейлиста'
        playlist_play = 'Добавляет плейлист в очередь и начинает воспроизведение'
        playlist_create = 'Создаёт плейлист'
        playlist_delete = 'Удаляет существующий плейлист'
        playlist_add = 'Добавляет песню в существующий плейлист'
        playlist_list = 'Перечисляет песени в существующем плейлисте'
        playlist_remove = 'Удаляет песню из существующего плейлиста'


    class phrases():
        not_connected = 'Я не присоединён ни к какому голосовому каналу'
        wait = 'Пожалуйста подождите, пока остальные участники дослушают музыку'
        Song = 'Песня'
        Playlist = 'Плейлист'
        not_found = 'не найден'

        ensure_voice_not_in_voice = 'Вы должны присоедениться к голосовому каналу, для использования этой команды'

        extract_info_youtube_error = 'Ошибка с сервисами YouTube, повторите попытку'

        play_song_youtube_error = 'Ошибка с сервисами YouTube, повторите попытку'
        play_song_now_playing = 'Сейчас играет'

        join_unnecessary_arguments = 'Эта командо не принимает аргументов'
        join_connected = 'Я присоединился к'
        join_wait = wait

        leave_unnecessary_arguments = join_unnecessary_arguments
        leave_disconnect = 'Я отсоединился от'
        leave_wait = wait
        leave_not_connected = not_connected

        play_playlist_not_supported = 'Ссылка на плейлист не поддерживается'
        play_songs_from = 'песни из'
        play_added_to_queue = 'добавленны в очередь'
        play_wait = wait
        play_song = Song
        play_songs_added_to_queue = 'песни добавленны в очередь'

        pause_unnecessary_arguments = join_unnecessary_arguments
        pause_already_pause = 'Нельзя поставить на паузу, то что уже на паузе'
        pause_not_playing = 'Нельзя поставить на паузу, так как я не играю музыку'
        pause_wait = wait
        pause_not_connected = 'Нельзя поставить на паузу, когда я не присоединился к голосовому каналу'

        resume_unnecessary_arguments = join_unnecessary_arguments
        resume_wait = wait
        resume_resumed = 'Возобновляю музыку'
        resume_already_resumed = 'Музыка уже играет'
        resume_not_music = 'Не могу возобновить, так как музыки нет'
        resume_not_connected = 'Нельзя возобновить, когда я не присоединился к голосовому каналу'

        stop_unnecessary_arguments = join_unnecessary_arguments
        stop_wait = wait
        stop_stoped = 'Останавляваю музыку'
        stop_no_music = 'Нельзя остановить то, что не играет'
        stop_not_connected = 'Нельзя остановить музыку, я и так не в голосовом канале'

        skip_wait = wait
        skip_empty_queue = 'Музыкакальная очередь пуста'
        skip_skipped = 'Пропущенно'
        skip_the_queue_only_have = 'В очереди только'
        skip_more_than_that = 'песен, но вы указали больше чем это'
        skip_not_connected = not_connected

        volume_not_connected = not_connected
        volume_wait = wait
        volume_no_arg = 'Пожалуйста укажите громкость, которую вы хотите'
        volume_changed = 'Громкость музыки изменена до'
        volume_max = 'Громкость не должна превышать 300%'

        queue_not_using = 'Вы не используйте музыку'
        queue_empty = 'Музыкакальная очередь пуста'
        queue_name = '**Музыкальная очередь**'
        queue_now_playing = 'Сейчас играет'
        queue_entries = 'Записи'
        queue_repeating = 'Повторение'
        queue_volume = 'Громкость'
        queue_page = 'Страница'
        queue_of = 'из'
        queue_not_exist = 'Страница которую вы указали не существует'
        queue_not_connected = not_connected

        dequeue_arg = 'Эта команда принимает только один аргумент'
        dequeue_wait = wait
        dequeue_song = Song
        dequeue_removed = 'удаленна из музыкальной очереди'
        dequeue_music = 'В музыкальной очереди'
        dequeue_more_than_that = 'песен, но вы указали больше чем это'
        dequeue_not_connected = not_connected

        clearqueue_arg = 'Эта команда принимает только один аргумент'
        clearqueue_wait = wait
        clearqueue_cleared = 'Очередь очищенна'
        clearqueue_not_connected = not_connected

        loop_wait = wait
        loop_repeat_all = 'Повторение всех песен в музыкальной очереди'
        loop_repeat_one = 'Повторение текущей песни в музыкальной очереди'
        loop_repeat_off = 'Повторение песен теперь выключено'
        loop_incorrect_arg = 'Пожалуйста, используйте правильный аргумент'
        loop_not_connected = not_connected

        playlist_no_in_guild = 'На этом сейвере еще не созданны плейлисты'
        playlist_on_server = 'Плейлисты на сервере'
        playlist_page = 'Страница'
        playlist_of = 'из'

        playlist_play_playlist = Playlist
        playlist_play_not_found = not_found
        playlist_play_added_to_queue = 'добавленна в очередь'
        playlist_play_wait = wait

        playlist_create_playlist = Playlist
        playlist_create_created = 'создан'
        playlist_create_already_exist = 'Плейлист с таким же названием уже су'

        playlist_delete_playlist = Playlist
        playlist_delete_not_found = not_found
        playlist_delete_deleted = 'удалён'

        playlist_add_not_supported = 'Ссылка на плейлист не поддерживается'
        playlist_add_song = Song
        playlist_add_added_to = 'добавленна в'
        playlist_add_songs_added_to = 'песни добавленны в'
        playlist_add_not_found = not_found
        playlist_add_note = 'Примечание'  # Подсказка
        playlist_add_note_content = 'Попробйуте добавить " " к имени вашего плейлиста'

        playlist_remove_song = Song
        playlist_remove_deleted_from = 'удалёна из'
        playlist_remove_the_playlist_have = 'В плейлисте'
        playlist_remove_more_than_that = 'песен, но вы указали больше, чем это'
        playlist_remove_playlist = Playlist
        playlist_remove_not_found = not_found

        playlist_list_empty = 'Плейлист пуст'
        playlist_list_Page = 'Старница'
        playlist_list_of = 'из'
        playlist_list_note = 'используйте .playlist list [имя плейлиста] [старница]'
        playlist_list_page_not_exist = 'Указанная вами страница не существует'
        playlist_list_playlist_not_exist = 'Плейлист не существует\nПримечание: попробуйте добавить " " к имени вашего плейлиста'  # \n означает перенос строки, его нетрогай!!!!!!!!!!

        on_ready_restarted = 'Я перезагрузился, играю последнюю песню из очереди'


    class errors():
        play_error = 'Команде play также нужна ссылка или ключевое слово для работы'

        dequeue_error = 'Пожалуйста, используйте правильный аргумент'

        add_error = 'Пожалуйста, укажите правильный аргумент'

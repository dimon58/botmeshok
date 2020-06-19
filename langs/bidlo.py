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
        dequeue  ='Удаляет песню из очереди'
        clearqueue='Очищает очередь воспроизведения'
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
        Song = 'Песня ебать'
        Playlist = 'Плейлист ебать'
        not_found = 'искал, искал нет нихуя, может ты найдёшь придурошный'

        ensure_voice_not_in_voice = 'Ты ебать выйди со мной раз на раз в голосовой канал, а не в текстовом пиши'

        extract_info_youtube_error = 'Не повезло, не фортануло пацанчик'

        play_song_youtube_error = 'There is an error with Youtube service, retrying'
        play_song_now_playing = 'Вот твоя хуита, слушай долбоёб'

        join_unnecessary_arguments = 'Сначала свиней ебать научись, а потом уже ботом управляй.'
        join_connected = 'Появился пидорас'
        join_wait = 'Охуел чтоли быдло. Пацанов надо уважать.'

        leave_unnecessary_arguments = join_unnecessary_arguments
        leave_disconnect = 'Съебался от вас нахуй'
        leave_wait = join_wait
        leave_not_connected = 'Пиздооооооооооооооооооос, ты меня выбесилю'

        play_playlist_not_supported ='Ты по нормальному пиши, а не по-пидорски.'
        play_songs_from = 'песни из твоего унитаза'
        play_added_to_queue = 'Захуячил твои говнопесни в очередь'
        play_wait = join_wait
        play_song = 'Песня-хуесня'
        play_songs_added_to_queue = 'заебашил твоё говно'

        pause_unnecessary_arguments = join_unnecessary_arguments
        pause_already_pause = 'Где только таких имбецилов берут?'
        pause_not_playing = 'Сказочный долбоёб'
        pause_wait = join_wait
        pause_not_connected = 'Ебалай, просто ебалай'

        resume_unnecessary_arguments = join_unnecessary_arguments
        resume_wait = join_wait
        resume_resumed = 'Продолжаю играть твою парашу'
        resume_already_resumed = 'Ты шо еблан?'
        resume_not_music = 'Пиздец ты конченый.'
        resume_not_connected = 'Выблядок ёбаный.'

        stop_unnecessary_arguments = join_unnecessary_arguments
        stop_wait = join_wait
        stop_stoped= 'Пошёл срать'
        stop_no_music = 'Ты еблан?'
        stop_not_connected = 'Точно еблан'

        skip_wait = join_wait
        skip_empty_queue = 'Нихуя нет идиот'
        skip_skipped = 'Пропустили эту ебалу,наконец-то.'
        skip_the_queue_only_have = 'Дохуя хочешь дебил'
        skip_more_than_that = 'У нас тут всего нихуя. Сам посмотри'
        skip_not_connected = 'Да меня, блядь, даже на месте нет.'

        volume_not_connected = 'Не на месте я'
        volume_wait = join_wait
        volume_no_arg = 'Циферки напиши блядь'
        volume_changed='Захуячил нужную громкость'
        volume_max='Ты чо хочешь чтобы у меняя кровь из ушей пошла'

        queue_not_using = 'Ты хуесос или пидорас?'
        queue_empty = 'Вован всё схавал.'
        queue_name = '**Music Queue**'
        queue_now_playing = 'Сейчас хуярит'
        queue_entries = 'Записи-хуяписи'
        queue_repeating = 'Повторяю для глухих долбоёбов'
        queue_volume = 'Громкость-хуёмкость'
        queue_page = 'Страничка=хуичка'
        queue_of = 'из'
        queue_not_exist = 'Не существет этой ебалы'
        queue_not_connected = not_connected

        dequeue_arg = 'В других обозначениях надо придурок'
        dequeue_wait = wait
        dequeue_song = 'Песня-хуесня'
        dequeue_removed = 'выкинул нахуй'
        dequeue_music = 'Только такая хуета есть'
        dequeue_more_than_that = 'пиздец много'
        dequeue_not_connected = not_connected

        clearqueue_arg = 'один блядь'
        clearqueue_wait = wait
        clearqueue_cleared = 'Вычистил это говно'
        clearqueue_not_connected = not_connected

        loop_wait=wait
        loop_repeat_all='Давай по новой всё хуйня'
        loop_repeat_one='Заебала эта ебатория'
        loop_repeat_off= 'Не работает это говно'
        loop_incorrect_arg='По-человечески прошу:пиши нормально мудак'
        loop_not_connected=not_connected

        playlist_no_in_guild =  'Нихуя не создал, чтобы чо то просить'
        playlist_on_server = 'Тупое говно'
        playlist_page= 'Страница ебать'
        playlist_of='из'

        playlist_play_playlist='Ебучий плейлист'
        playlist_play_not_found='из за лупы Джорджа нихуя не видно'
        playlist_play_added_to_queue='присобачил'
        playlist_play_wait=wait

        playlist_create_playlist = Playlist
        playlist_create_created = 'заебашил'
        playlist_create_already_exist = 'Совсем чтоли фантазии нет, свиноёб,?'

        playlist_delete_playlist = Playlist
        playlist_delete_not_found = not_found
        playlist_delete_deleted = 'Выпилил нахуй'

        playlist_add_not_supported = 'Бля, а можно норм ссылочку'
        playlist_add_song = Song
        playlist_add_added_to = 'Добавил эту залупу в'
        playlist_add_songs_added_to = 'Песни-хуесни добавлены'
        playlist_add_not_found = not_found
        playlist_add_note = 'Ну бля, вот так вот'  # Подсказка
        playlist_add_note_content = 'Попробуй добавить" " в свой ебучий плейлист имя'

        playlist_remove_song = Song
        playlist_remove_deleted_from = 'выпилил эту хуету из'
        playlist_remove_the_playlist_have = 'Плейлиста уже есть запах говна, а также'
        playlist_remove_more_than_that = 'ну не дохуя-ли, а?'
        playlist_remove_playlist = Playlist
        playlist_remove_not_found = not_found

        playlist_list_empty = 'Пусто нахуй'
        playlist_list_Page = 'Страница ебать её в рот'
        playlist_list_of = 'из'
        playlist_list_note = 'use .playlist list [playlist name] [page]'
        playlist_list_page_not_exist = 'Сынок ёбаный, ты куда пишешь?'
        playlist_list_playlist_not_exist = 'The playlist does not exist\nNote: Try adding " " to your playlist name'  # \n означает перенос строки, его нетрогай!!!!!!!!!!

        on_ready_restarted = 'Здарова педики, играю старую парашу'

    class errors():
        play_error = 'Бля, ну попробуй добавить внятные слова, а не мычание.'

        dequeue_error = 'Давай по новой, всё хуйня'

        add_error = 'Бля, ну тебя просили, а ты опять насрал.'
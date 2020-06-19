class Music():
    class descriptions():
        join = 'Connects to your voice channel'
        leave = 'Disconnects from your voice channel'
        play = 'Playing music from YouTube'
        pause = 'Pauses music'
        resume = 'Resumes music'
        stop = 'Stops music'
        skip = 'Skips a song from queue'
        volume = 'Changes volume (maximum=300)'
        queue = 'Shows your play queue'
        dequeue = 'Removes song drom queue'
        clearqueue = 'Clears queue'
        loop = 'Toggles between cycling all, one or turns it off'
        playlist = 'Access to playlist features'
        playlist_play = 'Adds a playlist to the queue and starts playing'
        playlist_create = 'Creates playlist'
        playlist_delete = 'Delets an exesting playlist'
        playlist_add = 'Adds a song to an existing playlist'
        playlist_list = 'Lists songs from an existing playlist'
        playlist_remove = 'Deleted a song from an existing playlist'


    class phrases():
        not_connected = 'Bot was not connected to any voice channel'
        wait = 'Please wait, until people are listening'
        Song = 'Song'
        Playlist = 'Playlist'
        not_found = 'not found'

        ensure_voice_not_in_voice = 'You should join the voice channel to use this command'

        extract_info_youtube_error = 'There is an error with Youtube service, please try again'

        play_song_youtube_error = 'There is an error with Youtube service, retrying'
        play_song_now_playing = 'Now playing'

        join_unnecessary_arguments = 'This command does not take in any other argument'
        join_connected = 'Bot connected to'
        join_wait = wait

        leave_unnecessary_arguments = join_unnecessary_arguments
        leave_disconnect = 'Bot disconnected from'
        leave_wait = wait
        leave_not_connected = 'Bot was not connected to any voice channel'

        play_playlist_not_supported = 'This playlist link is not supported'
        play_songs_from = 'songs from'
        play_added_to_queue = 'added to queue'
        play_wait = wait
        play_song = 'Song'
        play_songs_added_to_queue = 'songs added to queue'

        pause_unnecessary_arguments = join_unnecessary_arguments
        pause_already_pause = 'Cannot pause while bot was already paused'
        pause_not_playing = 'Cannot pause while bot was not playing music'
        pause_wait = wait
        pause_not_connected = 'Cannot pause while bot was not connected to any voice channel'

        resume_unnecessary_arguments = join_unnecessary_arguments
        resume_wait = wait
        resume_resumed = 'Resumed music'
        resume_already_resumed = 'Cannot resume if music is already playing'
        resume_not_music = 'Cannot resume if there is no music to play'
        resume_not_connected = 'Cannot resume while bot was not connected to any voice channel'

        stop_unnecessary_arguments = join_unnecessary_arguments
        stop_wait = wait
        stop_stoped = 'Stopped playing music'
        stop_no_music = 'Cannot stop if no music is playing'
        stop_not_connected = 'Cannot stop while bot was not connected to any voice channel'

        skip_wait = wait
        skip_empty_queue = 'The music queue is empty'
        skip_skipped = 'Skipped'
        skip_the_queue_only_have = 'The queue only have'
        skip_more_than_that = 'songs, but you specified more than that'
        skip_not_connected = 'Bot was not connected to any voice channel'

        volume_not_connected = not_connected
        volume_wait = wait
        volume_no_arg = 'Please specify the volume that you want'
        volume_changed = 'Music volume changed to'
        volume_max = 'Volume cannot exceed 300'

        queue_not_using = 'You are not using music'
        queue_empty = 'The music queue is empty'
        queue_name = '**Music Queue**'
        queue_now_playing = 'Now Playing'
        queue_entries = 'Entries'
        queue_repeating = 'Repeating'
        queue_volume = 'Volume'
        queue_page = 'Page'
        queue_of = 'of'
        queue_not_exist = 'The page you specified does not exist'
        queue_not_connected = not_connected

        dequeue_arg = 'This command only takes in one argument'
        dequeue_wait = wait
        dequeue_song = Song
        dequeue_removed = 'removed from music queue'
        dequeue_music = 'The music queue have'
        dequeue_more_than_that = 'songs, but you specified more than that!'
        dequeue_not_connected = not_connected

        clearqueue_arg = 'This command only takes in one argument'
        clearqueue_wait = wait
        clearqueue_cleared = 'Queue cleared'
        clearqueue_not_connected = not_connected

        loop_wait = wait
        loop_repeat_all = 'Repeating all songs in the music queue'
        loop_repeat_one = 'Repeating the current song in the music queue'
        loop_repeat_off = 'Repeating song is now off'
        loop_incorrect_arg = 'Please use the correct argument'
        loop_not_connected = not_connected

        playlist_no_in_guild = 'There is no playlist created in this guild'
        playlist_on_server = 'Playlists on the server'
        playlist_page = 'Page'
        playlist_of = 'of'

        playlist_play_playlist = Playlist
        playlist_play_not_found = not_found
        playlist_play_added_to_queue = 'added to queue'
        playlist_play_wait = wait

        playlist_create_playlist = Playlist
        playlist_create_created = 'created'
        playlist_create_already_exist = 'A playlist with the same name already exist'

        playlist_delete_playlist = Playlist
        playlist_delete_not_found = not_found
        playlist_delete_deleted = 'deleted'

        playlist_add_not_supported = 'This playlist link is not supported'
        playlist_add_song = Song
        playlist_add_added_to = 'added to'
        playlist_add_songs_added_to = 'songs added to'
        playlist_add_not_found = not_found
        playlist_add_note = 'Note'
        playlist_add_note_content = 'Try adding " " to your playlist name'

        playlist_remove_song = Song
        playlist_remove_deleted_from = 'deleted from'
        playlist_remove_the_playlist_have = 'The playlist have'
        playlist_remove_more_than_that = 'songs, but you specified more than that'
        playlist_remove_playlist = Playlist
        playlist_remove_not_found = not_found

        playlist_list_empty = 'The playlist is empty'
        playlist_list_Page = 'Page'
        playlist_list_of = 'of'
        playlist_list_note = 'use .playlist list [playlist name] [page]'
        playlist_list_page_not_exist = 'The page you specified does not exist'
        playlist_list_playlist_not_exist = 'The playlist does not exist\nNote: Try adding " " to your playlist name'

        on_ready_restarted = 'I was restarted, playing from the most recent song in queue'


    class errors():
        play_error = 'The play command also need a link or search keyword to work'

        dequeue_error = 'Please use the correct argument'

        add_error = 'Please specify the correct argument'

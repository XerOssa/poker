def waiting_room_view(request):
    # request.session.clear()

    form_config_table_data = {}
    file_path = 'poker_app/config_players.txt'
    config_players = read_config(file_path)

    players = players_list(config_players)
    initial_data = {}
    if request.method == 'POST':
        form = HeroForm(request.POST)
        form_config_table = GameConfigForm(request.POST)  # Sprawdź, czy POST zawiera dane

        # Jeśli POST nie zawiera kluczowych wartości, ustaw je ręcznie na domyślne
        if not request.POST.get('initial_stack'):
            request.POST = request.POST.copy()  # Musisz skopiować POST, bo jest niemutowalny
            request.POST['initial_stack'] = 200
        if not request.POST.get('small_blind'):
            request.POST['small_blind'] = 5
        if not request.POST.get('ante'):
            request.POST['ante'] = 0

        # Teraz sprawdź poprawność formularza
        if form_config_table.is_valid():
            config_data = form_config_table.cleaned_data
            form_config_table_data = {
                'initial_stack': config_data.get('initial_stack'),
                'small_blind': config_data.get('small_blind'),
                'ante': config_data.get('ante'),
            }
            request.session['form_config_table'] = form_config_table_data

            game_config = {
                'initial_stack': form_config_table_data.get('initial_stack'),
                'small_blind': form_config_table_data.get('small_blind'),
                'ante': form_config_table_data.get('ante'),
                'ai_players': players
            }
            request.session['game_config'] = game_config
            return redirect('waiting_room')

        if form.is_valid():
            hero = form.save(commit=False)
            hero.save()

            display_id = len(players)
            players.append({
                'idx': display_id,
                'type': 'human',
                'name': hero.name,
            })

            request.session['players'] = players
            request.session['hero'] = {'name': hero.name}
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'poker', {
                    'type': 'register_player',
                    'message': {
                        'name': hero.name,
                    }
                }
            )
            return redirect('hero_registration')
        else:
            print(form_config_table.errors)
    else:
        form = HeroForm()
        if 'form_config_table' in request.session:
            initial_data = request.session['form_config_table']
        
        form_config_table = GameConfigForm(initial=initial_data)

    return render(request, 'waiting_room.html', {
        'form': form,
        'initial_data': initial_data,
        'players': players,
    })

# def charts(request):
#     FILES_PATH = 'hh/*.txt'
#     hands = process_poker_hand(FILES_PATH)

#     save_to_csv(hands)
#     df = pd.read_csv('poker_hand.csv')
#     df['cumulative_win_loss'] = df['win_loss'].cumsum()
#     plt.figure(figsize=(15, 4))
#     plt.plot(df.index, df['cumulative_win_loss'])
#     plt.title('Wykres sumy kumulacyjnej win_loss')
#     plt.xlabel('Numer rozdania')
#     plt.ylabel('Suma kumulacyjna win_loss')
#     plt.grid(True)

#     plot_filename = 'poker_hand.png'
#     plot_path = os.path.join(settings.MEDIA_ROOT, plot_filename)
#     # plot_path = os.path.join('media', 'poker_hand.png')

#     plt.savefig(plot_path)
#     plt.close()

#     plot_url = os.path.join(settings.MEDIA_URL, plot_filename)
#     return render(request, 'charts.html', {'plot_url': plot_url})
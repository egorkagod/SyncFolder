import os

# current_directory = os.chdir('C:\Users\pirat\OneDrive\Рабочий стол\SyncFolder')
# name = input('Укажите имя папки: ')
# os.rename('SyncFolder', 'MagicFolder')

directory, filename = os.path.split(r'C:\Users\pirat\OneDrive\Рабочий стол\SyncFolder')
print(directory, filename)

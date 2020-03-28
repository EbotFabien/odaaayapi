from app import createapp

app = createapp('dev')
name = '''
                                   (api)
 ███▄    █ ▓█████  █     █░  ██████ 
 ██ ▀█   █ ▓█   ▀ ▓█░ █ ░█░▒██    ▒ 
▓██  ▀█ ██▒▒███   ▒█░ █ ░█ ░ ▓██▄   
▓██▒  ▐▌██▒▒▓█  ▄ ░█░ █ ░█   ▒   ██▒
▒██░   ▓██░░▒████▒░░██▒██▓ ▒██████▒▒
░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▓░▒ ▒  ▒ ▒▓▒ ▒ ░
░ ░░   ░ ▒░ ░ ░  ░  ▒ ░ ░  ░ ░▒  ░ ░
   ░   ░ ░    ░     ░   ░  ░  ░  ░  
         ░    ░  ░    ░          ░  
 ~ By Leslie Etubo T, E. Fabien, Samuel Klein, Marc.

'''
if __name__ == "__main__":
    print(name)
    app.run(
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG'),
        ssl_context='adhoc'
    )

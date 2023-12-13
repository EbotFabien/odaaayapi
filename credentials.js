{
    "metadata": {
     "language_info": {
      "codemirror_mode": {
       "name": "ipython",
       "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.8.1"
     },
     "orig_nbformat": 4,
     "kernelspec": {
      "name": "python3",
      "display_name": "Python 3.8.1 64-bit ('3.8.1': pyenv)"
     },
     "interpreter": {
      "hash": "4df238aaac2c363f13891e4c0f66365f931fa9ecd49f63b6568efd3ec4286424"
     }
    },
    "nbformat": 4,
    "nbformat_minor": 2,
    "cells": [
     {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
       "# connect to odaaay server\n",
       "# IP: 104.238.191.159\n",
       "# user: odaaaynuxt, f"
      ]
     },
     {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
       "ssh odaaaynuxt@104.238.191.159\n",
       "\n",
       "# password will be demanded\n",
       "# You will be placed on the odaaaynuxt user desktop. This user is a superuser\n",
       "# Don't do any irreversible action.\n",
       "# You will see this folder structure\n",
       "\n",
       "data  nltk_data  odaaayapi  odaaayapp\n",
       "\n",
       "# To go back to desktop\n",
       "\n",sudo systemctl restart socket.service
       "cd ~\n",
       "\n",
       "# -- data | useless directory but don't delete\n",
       "# -- nltk_data | Natural Language support files\n",
       "# -- odaaayapi | contains odaaay flask API server\n",
       "# -- odaaayapp | contains nuxt project primes section\n",
       "\n",
       "odaaaynuxt@Alpha_Odaaay:~$ ls -l\n",
       "total 16\n",
       "drwxrwxr-x  3 odaaaynuxt odaaaynuxt 4096 Nov 28  2020 data\n",
       "drwxrwxr-x  3 odaaaynuxt odaaaynuxt 4096 Nov  9  2020 nltk_data\n",
       "drwxrwxr-x  4 odaaaynuxt odaaaynuxt 4096 Nov  5  2020 odaaayapi\n",
       "drwxrwxr-x 18 odaaaynuxt odaaaynuxt 4096 Nov 29  2020 odaaayapp\n",
       "\n",
       "# To browse project\n",
       "\n",
       "odaaaynuxt@Alpha_Odaaay:~$ cd odaaayapi/\n",
       "odaaaynuxt@Alpha_Odaaay:~/odaaayapi$ ls\n",
       "# app  server\n",
       "# Make sure you activate the virtual env before pip install -r requirements.txt\n",
       "odaaaynuxt@Alpha_Odaaay:~/odaaayapi$ source server/bin/activate\n",
       "\n",
       "# To deactivate type \n",
       "deactivate\n",
       "\n",
       "# To clone odaaayapi on your PC use\n",
       "\n",
       "git clone ssh://odaaaynuxt@104.238.191.159/~/odaaayapi/app/odaaayapi.git\n",
       "# Password will be demanded use the odaaaynuxt user's password.\n",
       "# To clone odaaayapp on your PC use\n",
       "git clone ssh://odaaaynuxt@104.238.191.159/~/odaaayapp/odaaay.git\n",
       "\n",
       "\n",
       "\n", 
       "# There are two services that run the api and redis\n",
       "sudo nano /etc/systemd/system/odaaayapi.service\n",
       "sudo nano /etc/systemd/system/redisrq.service\n",
       "sudo nano /etc/systemd/system/redis.service\n",
       "\n",
       "# After pushing to server, make sure you restart the service\n",
       "\n",
       "sudo systemctl restart odaaayapi.service\n",
       "sudo systemctl restart [servicename].service\n",
       "\n",
       "# To see status of any service \n",
       "\n",
       "sudo systemctl status odaaayapi.service\n",
       "\n",
       "# To connect to Postgresql, You can use Dbeaver\n",
       "\n",
       "sudo nano /etc/postgresql/11/main/pg_hba.conf\n",
       "sudo nano /etc/postgresql/11/main/postgresql.conf\n",
       "# Postgres configs\n",
       "\n",
       "9|!e!R.{S4^8ttt\n",
       "\n",
       "# Data importing and exporting\n",
       "psql -U postgres news < dbexport.sql\n",
       "psql -U postgres -W odaaayAdmin news < dbexport.sql\n",
       "psql -U postgres -W  news < dbexport.sql\n",
       "sudo systemctl restart postgresql\n",
       "psql -U postgres -W  news < dbexport.sql\n",
       "\n",
       "# To manage odaaay nuxt app\n",
       "\n",
       "# To stop pm2\n",
       "pm2 stop\n",
       "pm2 stop 0\n",
       "\n",
       "# To start pm2\n",
       "pm2 start\n",
       "pm2 ls\n",
       "pm2 start npm -- start\n",
       "\n",
       "# To reload/restart nginx\n",
       "sudo sytemctl reload nginx\n",
       "\n",/home/odaaaynuxt/ssl/odaaay_com.crt;
       "sudo systemctl status odaaayapi\n",
       "sudo nano /etc/nginx/sites-available/odaaay.com"
      ]
     }
    ]
   }

 
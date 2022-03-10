<div align="center">

# StudyRooms

 A website where User can create Rooms and multiple users can Join and Chat about the topic for which room was created. For self learning purpose.
 <hr/>
</div>

 <table width="100%"> 
<tr>
<td width="50%">   
<br/>   
<p align="center">
  Home
</p>
<img src="./images/home-screenshot.png" alt="Study Rooms app Home-screenshot">
</td> 
<td width="50%">
<br/>
<p align="center">
  Room Conversation
</p>
<img src="./images/room-screenshot.png" alt="Study Rooms app Room-screenshot">  
</td>
</table>
 
 Project made in Python and the Django framework

### Running the App

1. Create a virtual environment (Optional) :

```bash
# Let's install virtualenv first
pip install virtualenv

# Then we create our virtual environment
virtualenv envname  #django_env

# Activate the virtual environment
envname\scripts\activate  #django_env\Scripts\activate.bat
```

2. Install the requirements :

```bash
pip install -r requirements.txt
```
3. To run the App, we use :

```bash
python manage.py runserver
```
> ⚠ Then, the development server will be started at http://127.0.0.1:8000/
# Optometry Office Management

**Created with Django in Python**

---

📌 **Project Founder**  
Optometrist Mehdi Aria  

---

🎯 **Goals**  
Open-source programming can help expand electronic aspects of optometry.  


---

⏳ **Project Status:** 
- [█████-----] In Progress
  
---

📬 **Contact Me**  
- Telegram: [@mehdiartl](https://t.me/mehdiartl)  
- Instagram: [@mehdiaria.ir](https://instagram.com/mehdiaria.ir)  
- Email: [mehdiariatwt@gmail.com](mailto:mehdiariatwt@gmail.com)  

---


## ⚙️ Installation Steps

Follow these steps to set up the project locally:

### Step 1: Download and Install Anaconda
- Download Anaconda for your operating system from [here](https://www.anaconda.com/products/distribution).  
- Follow the installation instructions.

---

### Step 2: Create and Activate a Virtual Environment
In Anaconda Powershell Prompt write codes below and read and accept all questions.
```bash
 conda create -n optometry python=3.11
 conda activate optometry

```
every where you want to use server  (in Anaconda Powershell Prompt not CMD)  also after installation of server you should first use:
```
conda activate optometry
```
---

### Step 3:clone the repo:
Download Git for Windows from [here](https://git-scm.com/downloads/win).<br>
You can also download Git for Linux from [here](https://git-scm.com/downloads/linux)(if you have linux operation system).<br>
In Windows run Git CMD or Command Prompt (cmd not anaconda powershell prompt), and in Linux (e.g., Ubuntu) use the terminal.<br>
Open CMD or GITCMD in Windows and enter the commands below.
```
   cd %USERPROFILE%\Desktop
   git clone https://github.com/mehdiro20/Opt_Office_Management MyProject


```
or in anaconda powershell after (installing git).
```
   cd desktop
   git clone https://github.com/mehdiro20/Opt_Office_Management MyProject
```
---

### Step 4: Install Dependencies
From this step please use Anaconda Powershell Prompt (in windows).(it's better to use windscribe)
```
   cd Desktop
   cd MyProject
   pip install -r requirements.txt

```
---
### Step 5: Run Database Migrations
```
   python manage.py migrate

```
---
### Step 6: Create a Superuser (Admin Account)

```
   python manage.py shell
```
then ...
```
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.get(username='mehdi').delete()
    exit()
```
then again after exit in Anaconda Powershell Prompt :
```  
   python manage.py createsuperuser

```
---
### Step 7: Start the Development Server

```
   python manage.py runserver

```
   

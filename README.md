# Optometry Office Management

**Created with Django in Python**

---

📌 **Project Founder**  
Mehdi Aria  

---

🎯 **Goals**  
Open-source programming can help expand electronic aspects of optometry.  


---

**  Project Status:** 
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
In Anaconda Powershell Prompt read and accept all questions.
```bash
- conda create -n optometry python=3.11
- conda activate optometry

```
---
### Step 3:clone the repo:
Download Git for Windows from [here](https://git-scm.com/downloads/win).<br>
You can also download Git for Linux from [here](https://git-scm.com/downloads/linux)(if you have linux operation system).<br>
Then in Windows run Git CMD or Command Prompt (cmd not anaconda powershell prompt), and in Linux (e.g., Ubuntu) use the terminal.
```
   git clone https://github.com/your-username/your-repo.git
   cd your-repo

```
---

### Step 4: Install Dependencies
From this step please use Anaconda Powershell Prompt (in windows)
```
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
    from django.contrib.auth.models import User
    User.objects.get(username='mehdi').delete()
    exit()
   python manage.py createsuperuser

```
---
### Step 7: Start the Development Server

```
   python manage.py runserver

```
   

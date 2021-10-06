

The Repositories has two items, one is a visualization tool, the other is our Evolutionary algorithm for droplet routing.

#### The visualization tool for a digital microfluidic chip droplet routing.

It is developed based on the python language and django framework, so to run it you need to install python and django and related dependency packages.

##### how to use?

Step 1:

1.Use pycharm run this project.

2.Use termianl: Go to the project folder and input:

```python
python manage.py runserver
```
Step 2:
Then open  Browser  to input the address : http://127.0.0.1:8000/index.html.

#### The  EA algorithm for droplet routing

**how to use?**

```
cd .\EAForDropletRouting\MyEA
python GA.py
```

Once you run the code, it will according to the default setting. You can add some parameters like "--ng=50" , you can find detailed parameter describe in **\EAForDropletRouting\arguments.py**.

##### Other things

We provide some experimental results to demonstrate, those data is at the floder **experiment_result**


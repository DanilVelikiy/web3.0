from django.db import models

from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    technology = models.CharField(max_length=20)
    image = models.FilePathField(path="/img")
    target = models.TextField(default=None, null=True)
    target = models.TextField(default=None , null=True)
    block_1_text = models.TextField(default=None, null=True)
    block_1_image = models.FilePathField(path="/img", default=None, null=True)
    block_2_text = models.TextField(default=None , null=True)
    block_2_image = models.FilePathField(path="/img" , default=None , null=True)
    block_3_text = models.TextField(default=None , null=True)
    block_3_image = models.FilePathField(path="/img" , default=None , null=True)
#    paragraph_txt_1 = models.TextField(default=None, null=True)
#    paragraph_img_1 = models.FilePathField(path="/img" , default=None , null=True)
    # сылку на гитхаб надо еще

import os
import  getopt
import sys
import getpass
import  subprocess
import paramiko
import zipfile
import pexpect
# 自动上传iOS脚本

#需要配置的东西  SDKConfig  没办法配置的东西就是需要这么多......还是很烦
class   SDKConfig:
        # framework路径
        basepath = "/Users/lotawei/Library/Developer/Xcode/DerivedData/Myworkspace-bkvekghszqryiagkxxttvtrudmlq/Build/Products/"
        taskdirlibs = ["RadiumSDK","SdkPlugin_AJ","SdkPlugin_PY","SdkPlugin_VK","SdkPlugin_FB"] #插件名 
    
        # 模拟器路径
        lmpaths = []
        # 真机路径
        phonepaths = []
        # 输出路径
        outpathdir = "/Users/lotawei/Desktop/RadiumsdkPro/RadiumSDK_IOS/RadiumPublish" #合成输出的路径
        # lincense
        lincensepath =  "/Users/lotawei/Desktop/RadiumsdkPro/RadiumSDK_IOS/RadiumPublish/LICENSE" #license文件路径 用于pod发布
        #服务器相关配置

        ips = "11.1.1.1" #自建服务器地址  上传相关
        username = "root?"
        pwd = "??????"
        serverrootpath = "/IOS_SDK" #pod 相关上传zip根路径
        taskversion = "1.0.0"


        @staticmethod

        def configpaths():
            for smipath in SDKConfig.taskdirlibs:
                SDKConfig.lmpaths.append("{0}Debug-iphonesimulator/{1}.framework".format(SDKConfig.basepath,smipath))
            for phopath in SDKConfig.taskdirlibs:
                SDKConfig.phonepaths.append("{0}Debug-iphoneos/{1}.framework".format(SDKConfig.basepath,phopath))

class  SDkPlugin:
      def  __init__(self,lmpath,phpath,outpath,libname):
            self.lmpath = lmpath
            self.phpath = phpath
            self.libname = libname
            self.outpath = outpath
      def   sdkinfo(self):
            print("{0}信息: *****************************\n".format(self.libname))
            print("模拟器路径:{0} \n真机路径:{1}\n合成路径:{2}\n".format( self.lmpath,self.phpath,self.outpath))
            print("{0}信息: *****************************\n".format(self.libname))

class  ZipTools:
    @staticmethod
    def zip_ya(startdir,file_news):



             file_news = startdir + '.zip'  # 压缩后文件夹的名字

             z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名

             for dirpath, dirnames, filenames in os.walk(startdir):

                 fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制


                 for filename in filenames:

                     z.write(os.path.join(dirpath, filename), fpath + filename)

             print('压缩成功')

             z.close()
class  AutoUploadSDK:

    tasks = []
    newtask = []
    uploadtaskfile = []
    @staticmethod
    def  start():
        SDKConfig.configpaths()
        AutoUploadSDK.occurtasks()
        AutoUploadSDK.mergesdk()
    # 从sdkconfig中生成插件
    @staticmethod
    def occurtasks():
        print("生成配置任务😁------------------------------😁")
        AutoUploadSDK.tasks = []
        AutoUploadSDK.newtask = []
        if len(SDKConfig.taskdirlibs) == 0 or len(SDKConfig.lmpaths) == 0  or len(SDKConfig.phonepaths) == 0:
            print("请正确配置sdkconfig")
            return

        i = 0
        for  sname in SDKConfig.taskdirlibs:
             mpath = SDKConfig.lmpaths[i]
             ppath = SDKConfig.phonepaths[i]
             outpath = "{0}".format(SDKConfig.outpathdir)

             sdkp = SDkPlugin(mpath,ppath,outpath,sname)
             AutoUploadSDK.tasks.append(sdkp)
             sdkp.sdkinfo()
             i = i + 1

    # 合成并生成新的插件
    @staticmethod
    def mergesdk():
        print("开启合成任务😢------------------------------😢\n\n")
        j = 0
        AutoUploadSDK.uploadtaskfile = []
        for  lib in AutoUploadSDK.tasks:
             print("————————————————————制作{0}".format(lib.libname))
             flagout =  os.system("cd {0}".format(SDKConfig.outpathdir))
             if flagout != 0 :
                print("请检查合成路径是否正确😭😭😭😭😭😭😭😭😭😭😭😭😭😭\n")
                return
             print("lipo -create {0}/{1} {2}/{3} -output {5}/{4}".format(lib.lmpath, lib.libname, lib.phpath, lib.libname,
                                                                         lib.libname, SDKConfig.outpathdir, lib.libname))
             taskflag =   os.system("lipo -create {0}/{1} {2}/{3} -output {5}/{4}".format(lib.lmpath,lib.libname,lib.phpath,lib.libname,lib.libname,SDKConfig.outpathdir,lib.libname))
             if  taskflag != 0 :
                 print("合成{0}😭😭😭😭😭😭😭😭😭😭😭😭😭😭出错了.........检查是否已经替换了的包 lipo -info 可查看\n".format(lib.libname))
                 return
             else           :
                 print("{0}合成完毕😊😊😊😊😊😊😊😊😊😊😊😊😊😊\n".format(lib.libname))
             supportosandsimulatorpath = "{0}/{1} ".format( SDKConfig.outpathdir, lib.libname)
             infoflag =   os.system("lipo -info {0}/{1} ".format( SDKConfig.outpathdir, lib.libname))
             if infoflag == 0 :
                 print("{0}支持模拟器和真机😊😊😊😊😊😊😊😊😊😊😊😊😊😊\n".format(lib.libname))

             isexist =  os.path.exists("{0}/{1}_publish".format(SDKConfig.outpathdir,lib.libname))
             if  isexist :
                 print("存在时替换")
                 os.system("cp -r {0} {1}/{2}_publish/{3}.framework".format(supportosandsimulatorpath,SDKConfig.outpathdir,lib.libname,lib.libname))
                 os.system(
                     "cp -r {0} {1}/{2}_publish".format(SDKConfig.lincensepath,
                                                        SDKConfig.outpathdir, lib.libname))
                 #压缩
                 # zipcmd = "zip -r  -1 -q -o {0} {1}_publish".format(lib.libname + "Core.zip",lib.libname
                 #                                                           )
                 # print(zipcmd)
                 #


                 ZipTools.zip_ya("{0}/{1}_publish".format(SDKConfig.outpathdir, lib.libname),
                                 "{0}v_{1}".format(lib.libname, SDKConfig.taskversion))

                 os.rename("{0}/{1}_publish.zip".format(SDKConfig.outpathdir, lib.libname),"{0}/{1}v_{2}.zip".format(SDKConfig.outpathdir,lib.libname, SDKConfig.taskversion))
                 # os.system("mv {0}_publish.zip {1}v_{2}.zip".format(lib.libname,lib.libname,SDKConfig.taskversion))
                 AutoUploadSDK.uploadtaskfile.append("{0}v_{1}.zip".format(lib.libname, SDKConfig.taskversion))
                 # taskpath = "{0}v_{1}.zip".format(lib.libname, SDKConfig.taskversion)
                 # AutoUploadSDK.upload(taskpath
             else :
                 os.system("mkdir {0}/{1}_publish".format(SDKConfig.outpathdir,lib.libname))
                 os.system("cp -r {0} {1}/{2}_publish/{3}.framework".format(lib.lmpath, SDKConfig.outpathdir, lib.libname, lib.libname))
                 print("{0}发布framework文件生成成功😊😊😊😊😊😊😊😊😊😊😊😊😊😊\n".format(lib.libname))
                 os.system(
                         "cp -r {0} {1}/{2}_publish".format(SDKConfig.lincensepath,
                                                                          SDKConfig.outpathdir, lib.libname))
                 #替换新的支持真机模拟器的
                 placecmd = os.system(
                     "cp -r {0} {1}/{2}_publish/{3}.framework".format(supportosandsimulatorpath, SDKConfig.outpathdir, lib.libname,
                                                                      lib.libname))
                 if placecmd == 0:
                     print("{0}支持模拟器和真机 framework 文件生成成功 😊😊😊😊😊😊😊😊😊😊😊😊😊😊\n".format(lib.libname))
                     #压缩
                     # os.system("zip -r -9 -o -q {0} {1}".format(lib.libname + "Core.zip",SDKConfig.outpathdir))

                     ZipTools.zip_ya("{0}/{1}_publish".format(SDKConfig.outpathdir, lib.libname),
                                     "{0}v_{1}".format(lib.libname,SDKConfig.taskversion))
                     AutoUploadSDK.uploadtaskfile.append("{0}v_{1}.zip".format(lib.libname, SDKConfig.taskversion))
                     # taskpath =  "{0}v_{1}.zip".format(lib.libname,SDKConfig.taskversion)
                     # AutoUploadSDK.upload(taskpath)

                 else:
                    print("{0}发布版本失败😭😭😭😭😭😭😭😭😭😭😭😭😭😭\n".format(lib.libname))
                    return

        j = j+1
        print("_____________________________*******************____________________________")

        print("成功制作完{0}个新的framework😊😊😊😊😊😊😊😊😊😊😊😊😊😊\n\n\n".format(j))

    @staticmethod
    def   upload(ziptaskpath):
             ssh = paramiko.SSHClient()
             ssh.load_system_host_keys()

             try:
                 ssh.connect(SDKConfig.ips, username=SDKConfig.username, password=SDKConfig.pwd)

                 print("连接已建立")
                 sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
                 sftp = ssh.open_sftp()
                 if os.path.isfile(ziptaskpath):
                    sftp.put(ziptaskpath,SDKConfig.serverrootpath)


                    print("{0}\n 文件已上传 \n".format(ziptaskpath))
                 else:
                     print("{0} 文件不存在 \n".format(ziptaskpath))
                 sftp.close()
                 ssh.close()
             except Exception as e:
                 print(e)
                 return
    @staticmethod
    def  createpodspec(podtask):
                specpath = "{0}/{1}.podspec".format(SDKConfig.outpathdir, podtask)

                isexist = os.path.exists(specpath)
                if isexist==false :
                    cmd = "pod spec create {0}".format(specpath)
                    os.system(cmd)
                #然后进行 模板 内容替换 加上当前发布需要的配置信息
                #生成新的podspec文件
                

    @staticmethod
    def modyfile(file, old_str, new_str):
        """
        替换文件中的字符串
        :param file:文件名
        :param old_str:就字符串
        :param new_str:新字符串
        :return:
        """
        file_data = ""
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                file_data += line
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_data)


    @staticmethod
    def    podlint(podtask):
             # /Users/lotawei/Desktop/RadiumsdkPro/RadiumSDK_IOS/RadiumPublish/SdkPlugin_FB.podspec
             # os.system("cd {0}".format(SDKConfig.outpathdir))
             cmd =  "pod spec lint  {0} --allow-warnings".format(podtask)
             print("执行.....{0}".format(cmd))
             flag =  os.system(cmd)
             if  flag != 0 :
                 print("{0} pod  lint  失败......".format(podtask))
                 return
             else :
                 print("{0} cocoapods验证成功........".format(podtask))
    @staticmethod
    def podpush(podtask):
        # /Users/lotawei/Desktop/RadiumsdkPro/RadiumSDK_IOS/RadiumPublish/SdkPlugin_FB.podspec
        # os.system("cd {0}".format(SDKConfig.outpathdir))
        cmd = "pod trunk push {0} --allow-warnings".format(podtask)
        print("执行.....{0}".format(cmd))
        flag = os.system(cmd)
        if flag != 0:
            print("{0} pod  push  失败......".format(podtask))
            return
        else:
            print("{0} cocoapods发布成功........".format(podtask))



AutoUploadSDK.start()  #开启合并文件等操作


for  podserres in AutoUploadSDK.uploadtaskfile:
     print(podserres)

     AutoUploadSDK.upload("{0}/{1}".format(SDKConfig.outpathdir,podserres))


#
# for   lin in AutoUploadSDK.tasks:
#      AutoUploadSDK.podlint("{0}/{1}.podspec".format(SDKConfig.outpathdir,lib.libname))
#      AutoUploadSDK.podpush("{0}/{1}.podspec".format(SDKConfig.outpathdir,lib.libname))

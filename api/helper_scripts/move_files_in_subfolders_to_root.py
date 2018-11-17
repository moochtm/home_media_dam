import os, shutil


##################################################################
# tests
##################################################################

def main():
    root_path = '/Users/home/Pictures/ORIGINALS/Google Photos Backup'

    print "==========================================================================================="
    print "scanning folder tree and moving files to root..."

    for root, dirs, files in os.walk(root_path, topdown=False):
        for name in files:
            print('File: %s' % os.path.join(root, name))
            target_path = os.path.join(root_path, name)
            if os.path.exists(target_path):
                i = 1
                file, extension = os.path.splitext(name)
                while os.path.exists(os.path.join(root_path, '%s-%s%s' % (file, i, extension))):
                    i += 1
                target_path = os.path.join(root_path, '%s-%s%s' % (file, i, extension))
            print '   moving to: %s' % target_path
            shutil.move(os.path.join(root, name), target_path)

    print "==========================================================================================="
    print "scanning folder tree and deleting empty folders..."

    for root, dirs, files in os.walk(root_path, topdown=False):
        if len(files) == 0:
            print 'Deleting empty folder: %s' % root
            shutil.rmtree(root)


if __name__ == "__main__":
    main()

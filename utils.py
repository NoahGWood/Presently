from database import db_session
from models import User, File, Presentation, PresentationUser
from file_manager import load_file_text, upload_file_from_txt
import uuid
import datetime

def FindPresentationFile(presentation):
    return db_session.query(File).filter(
        File.filepath.contains(presentation+'.txt')
        ).first()

def FindAllPresentationAudio(presentation):
    audios = []
    for pf in presentation.files:
        if 'audio' in pf.filetype:
            audios.append(pf)
    return audios

def FindAudioBySlide(audio_list, slide):
    """Returns the file for an approriate slide."""
    for each in audio_list:
        if 'audio{}'.format(slide) in each.filetype:
            return each
    return None
    
def FindPresentationOwnerByFile(pfile):
    return db_session.query(PresentationUser).filter(
        PresentationUser.presentation_id == pfile.presentation_id
        ).first()

def GetPresentationByFile(pfile):
    return db_session.query(Presentation).filter(
        Presentation.id == pfile.presentation_id
        ).first()


def UserCanAccessPresentation(user, pres_user):
    """Returns true if user can access presentation, false if not."""
    return user.id == pres_user.user_id

def AuthPresentation(user, presentation):
    """Handles authenticating user to presentation.
    
        Returns tuple (true, presentation, main file) if available
    """
    pres_file = FindPresentationFile(presentation)
    pres_user = FindPresentationOwnerByFile(pres_file)
    pres = GetPresentationByFile(pres_file)
    return UserCanAccessPresentation(user, pres_user), pres, pres_file


def NewPresentation(current_user, title, language, translate, genimages, text):
    fname = str(uuid.uuid4())
    write_text_file(fname, text)
    time = datetime.datetime.now()
    p = Presentation(title=title, ctime=time, mtime=time,
                     translate=translate, genimages=genimages)
    f = File(language=language, ctime=time, mtime=time,
             filepath="{}.txt".format(fname))
    p.files.append(f)
    curr_usr = db_session.query(User).filter(
        User.id == current_user.id).first()
    curr_usr.presentations.append(p)
    db_session.add(p)
    db_session.add(f)
    db_session.add(curr_usr)
    db_session.commit()
    return fname

def write_text_file(fname, text):
    """ Writes text to file fname"""
    upload_file_from_txt(fname+'.txt', text)


def GetText(filepath):
    """Returns the text of file"""
    txt = ''
    return load_file_text(filepath)

def GetVideos(presentation):
    vids = []
    for f in presentation.files:
        if f.ftype == 'video':
            vids.append(f)
    return vids
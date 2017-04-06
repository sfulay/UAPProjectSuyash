
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
#song = AudioSegment.from_wav("Austin/Word Recordings.wav")

listOfLetters = ['b','c','d','e','f','g','h','i','j','k','l','m']
def cutAudio(username, letter):    
    song = AudioSegment.from_wav("uploads/"+username+"/"+letter+"/"+letter+".wav")
    chunks = split_on_silence(song,
    # must be silent for at least half a second
        min_silence_len=300,

    # consider it silent if quieter than -16 dBFS
        silence_thresh=-45
    )
    for i,chunk in enumerate(chunks):
        #print len(chunks)
        #print letter
        #print letter+'/'+chunk+'{0}'+'.wav'.format(i)
        # print '{0}'
        # print '/Austin/'+letter
        # print '/Austin/'+letter+'/'
        # print chunk
        filePath = "uploads/"+username+ "/" + letter+'/'+'chunk'+str(i)+'.wav'
        #print filePath
        chunk.export(filePath.format(i), format="wav")

def removeOldFile(username, letter):
    os.remove("uploads/"+username+'/'+letter+'/'+letter+'.wav')
    #
    # song = AudioSegment.from_wav("Austin/b.wav")
    # chunks = split_on_silence(song,
    # # must be silent for at least half a second
    #     min_silence_len=300,
    #
    # # consider it silent if quieter than -16 dBFS
    #     silence_thresh=-45
    # )
    #
    # for i,chunk in enumerate(chunks):
    #     print len(chunks)
    #     chunk.export("Austin/b/chunk{0}.wav".format(i), format="wav")

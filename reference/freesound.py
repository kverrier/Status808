from freesound.__init__ import *
Freesound.set_api_key('31ac7f49d68644c4bfafaf8213eddbc5')

# Get sound info example
#print "Sound info:"
#print "-----------"
#s = Sound.get_sound(96541)
#print "Getting sound: " + s['original_filename']
#print "Url: " + s['url']
#print "Description: " + s['description']
#print "Tags: " + str(s['tags'])
#print "Preview (Low Quality) " + str(s['preview-lq-mp3'])
#print "\n"

# Get similar sounds example
#print "Similar sounds: "
#print "---------------"
#similar_sounds = s.get_similar()
#for sound in similar_sounds['sounds']:
    #print "\t- " + sound['original_filename'] + " by " + sound['user']['username']
#print "\n"

# Search Example
print "Searching for 'violoncello':"
print "----------------------------"
results = Sound.search(q="forgot",filter="duration:[1.0 TO 15.0]",sort="rating_desc", max_results="3")
print "Num results: " + str(results['num_results'])
print "\t ----- PAGE 1 -----"
for sound in results['sounds']:
    print "\t- " + sound['original_filename'] + " --> " + sound['preview-lq-mp3']
print "\n"


# Content based search example
#print "Content based search:"
#print "---------------------"
#results = Sound.content_based_search(f=".lowlevel.pitch.var:[* TO 20]",
    #t='.lowlevel.pitch_salience.mean:1.0 .lowlevel.pitch.mean:440',
    #fields="preview-hq-ogg,duration,tags,url",
    #max_results="15",
    #sounds_per_page="10")

#print "Num results: " + str(results['num_results'])
#for sound in results['sounds']:
    #print "\t- " + sound['url']
#print "\n"


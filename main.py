import StringIO
import json
import logging
import random
import urllib
import urllib2

# for random number
from random import randint

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '256416071:AAEzHq5tJZXqKdY3TXOunbsEntA5U7x9azo'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

def triggerAnswer(text,context):
    for ask in _ask[context]:
        if ask in text:
            return True
    return False

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text').lower()
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def posting(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if '/info' in text:
                posting('BaperBot adalah bot kekinian yang sangat sensitif dan gampang sekali baper.\n\nNama\t\t: BaperBot\nJenis kelamin\t\t: Laki-laki\nAgama\t\t: Islam\nHobi\t\t: stalking mantan, update status gak jelas\n\nVersion 1.0.1\nCreated by @sssandyad')
            elif text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif '/image' in text:
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())

        # CUSTOMIZE FROM HERE
        elif 'assalam' in text:
            reply('Waalaikumsalam')
        elif triggerAnswer(text,'ayo'):
            reply(_answer['ayo'][randint(0,len(_answer['ayo'])-1)])
        elif triggerAnswer(text,'main'):
            reply(_answer['main'][randint(0,len(_answer['main'])-1)])
        elif triggerAnswer(text,'mantan'):
            reply(_answer['mantan'][randint(0,len(_answer['mantan'])-1)])
        elif triggerAnswer(text,'baperbot'):
            if triggerAnswer(text,'baperbot_positif'):
                reply(_answer['baperbot_positif'][randint(0,len(_answer['baperbot_positif'])-1)])
            elif triggerAnswer(text,'baperbot_ejek'):
                reply(_answer['baperbot_ejek'][randint(0,len(_answer['baperbot_ejek'])-1)])
            elif triggerAnswer(text,'baperbot_salah'):
                reply(_answer['baperbot_salah'][randint(0,len(_answer['baperbot_salah'])-1)])
            elif triggerAnswer(text,'baperbot_pagi'):
                reply(_answer['baperbot_pagi'][randint(0,len(_answer['baperbot_pagi'])-1)])
            else:
                reply(_answer['baperbot'][randint(0,len(_answer['baperbot'])-1)])
        elif triggerAnswer(text,'baper'):
            reply(_answer['baper'][randint(0,len(_answer['baper'])-1)])
        elif triggerAnswer(text,'tertawa'):
            reply(_answer['tertawa'][randint(0,len(_answer['tertawa'])-1)])
        elif triggerAnswer(text,'tanya'):
            reply(_answer['tanya'][randint(0,len(_answer['tanya'])-1)])
        elif triggerAnswer(text,'pacar'):
            reply(_answer['pacar'][randint(0,len(_answer['pacar'])-1)])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)


_emot_grinning_face_with_smiling_eyes = u'\U0001F601'
_emot_face_with_tears_of_joy = u'\U0001F602'
_emot_smilling_face_with_open_mouth = u'\U0001F603'
_emot_smilling_face_with_open_mouth_and_smilling_eyes = u'\U0001F604'
_emot_smilling_face_with_open_mouth_and_cold_sweat = u'\U0001F605'
_emot_smilling_face_with_open_mouth_and_tightly_closed_eyes = u'\U0001F606'
_emot_winking_face = u'\U0001F609'
_emot_smilling_face_with_smilling_eyes = u'\U0001F60A'
_emot_face_savouring_delicious_food = u'\U0001F60B'
_emot_relieved_face = u'\U0001F60C'
_emot_smilling_face_with_heart_shapped_eyes = u'\U0001F60D'
_emot_smirking_face = u'\U0001F60F'
_emot_unamused_face = u'\U0001F612'
_emot_face_with_cold_sweat = u'\U0001F613'
_emot_pensive_face = u'\U0001F614'
_emot_confounded_face = u'\U0001F616'
_emot_face_throwing_a_kiss = u'\U0001F618'
_emot_kissing_face_with_closed_eyes = u'\U0001F61A'
_emot_face_with_stuck_out_tongue_and_winking_eye = u'\U0001F61C'
_emot_face_with_stuck_out_tongue_and_tightly_closed_eyes = u'\U0001F61D'
_emot_disappointed_face = u'\U0001F61E'
_emot_angry_face = u'\U0001F620'
_emot_pouting_face = u'\U0001F621'
_emot_crying_face = u'\U0001F622'
_emot_persevering_face = u'\U0001F623'
_emot_face_with_look_of_triumph = u'\U0001F624'
_emot_disappointed_but_relieved_face = u'\U0001F625'
_emot_fearful_face = u'\U0001F628'
_emot_weary_face = u'\U0001F629'
_emot_sleepy_face = u'\U0001F62A'
_emot_tired_face = u'\U0001F62B'
_emot_loudly_crying_face = u'\U0001F62D'
_emot_face_with_open_mouth_and_cold_sweat = u'\U0001F630'
_emot_face_screaming_in_fear = u'\U0001F631'
_emot_astonished_face = u'\U0001F632'
_emot_flushed_face = u'\U0001F633'
_emot_dizzy_face = u'\U0001F635'
_emot_face_with_medical_mask = u'\U0001F637'

_emot_musical_note = u'\U0001F3B5'
_emot_multiple_musical_notes = u'\U0001F3B6'
_emot_saxophone = u'\U0001F3B7'
_emot_guitar = u'\U0001F3B8'
_emot_musical_keyboard = u'\U0001F3B9'
_emot_violin = u'\U0001F3BA'

_emot_heart = u'\U00002764'
_emot_no_entry_sign = u'\U0001F6AB'

_answer = {
    'ayo': (
        'Ayook ' + _emot_grinning_face_with_smiling_eyes,
        'Lu ngajak gue?',
        'Males ah!',
        'Lah ayok. Gue harus gimana ini?',
        'Ajak yg lain aja. Gue lagi gak mood ' + _emot_pensive_face,
        'Maaf, gue lagi sibuk!',
        'Caranya gimana?',
        'Yok!',
        'Bentar ya sayang.. ',
        'Ayok ke mana sih??',
        'Sekarang?',
        'Lu sendiri aja sana! Gak usah ngajak2 gue lagi ' + _emot_loudly_crying_face,
        'Ayok2 aja sih kalo gue. Yang lain?'
    ),
    'main': (
        'Sorry ya, gue gak suka kalo main2. Gue maunya yang serius ' + _emot_face_with_stuck_out_tongue_and_tightly_closed_eyes,
        'Kok main2 sih? Gue butuhnya org yg mau serius ama gue ' + _emot_weary_face,
        'Main boleh, tapi perasaan cewek gak boleh dibuat mainan yaa ' + _emot_winking_face,
        'Main apa?',
        'Ayok main! ' + _emot_grinning_face_with_smiling_eyes,
        'Main2 terus nih kapan seriusnya ' + _emot_smilling_face_with_open_mouth_and_cold_sweat,
        'Gak bosen main ini terus? ' + _emot_smilling_face_with_open_mouth_and_cold_sweat,
        'Pengen main apa?',
        'Loh, lu kan kalah terus kalo main sama gue?',
        'Males ah. Kurang menantang permainannya ' + _emot_sleepy_face,
        'Gue temenin yah. Mau main apa? ' + _emot_grinning_face_with_smiling_eyes,
        'Main lagi? ' + _emot_smirking_face + ' Gue takut menang nih. Terlalu jago gue ' + _emot_smilling_face_with_open_mouth_and_tightly_closed_eyes,
        'Ayok main! Tapi kalau kalah lu jangan nangis lagi lho kyk kemaren ' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Main ayok! Yang kalah gak boleh baper! ' + _emot_face_with_stuck_out_tongue_and_tightly_closed_eyes,
        'Main lagi?? Kalahan gitu lho ' + _emot_unamused_face,
        'Ayo main kaka\' ' + _emot_grinning_face_with_smiling_eyes,
        'Main aja dulu. Nanti gue nyusul'
    ),
    'mantan': (
        'Gak usah nyebut2 kata mantan di depan gue! Baper gue!!! ' + _emot_angry_face,
        'Mantan mending ke laut aja!',
        'DILARANG sebut2 kata MANTAN biar gak baper!',
        'Baper nih gue tiba2 ingat mantan ' + _emot_pensive_face,
        'Duh jangan nyebut mantan po\'o rek ' + _emot_face_with_cold_sweat,
        _emot_musical_note + ' Oh di hati ini hanya engkau mantan terindah ' + _emot_multiple_musical_notes +' yang selalu kurindukan ' + _emot_musical_note + ' ' + _emot_saxophone
    ),
    'baperbot': (
        'Lo manggil gue?',
        'Yup baperbot, itulah gue. Bot paling baper sedunia ' + _emot_grinning_face_with_smiling_eyes,
        'Iya sayang?',
        'Lo panggil2 gue ada apa?',
        'Sapa sih lu panggil2 ' + _emot_angry_face,
        'Ada yang manggil gue?',
        '?'
    ),
    'baperbot_salah': (
        'Gue salah apa? ' + _emot_loudly_crying_face,
        'Maaf ' + _emot_pensive_face,
        'Oo gitu ya? jadi ini semua gara2 gue??',
        'Lo jahat banget sih ' + _emot_loudly_crying_face, 
        'Oke, fine!',
        'Terserah!',
        'Cape deh. Lagi2 gue yg salah ' + _emot_pensive_face,
        'Kok gue terus sih yang disalahin ' + _emot_angry_face,
        'Gue tahu gue salah. Tapi lu gak perlu juga pake nyolot gitu kan ' + _emot_loudly_crying_face,
        'Hmm.. gitu?',
        'Bisa gak kalau gak usah nyalah2in bot?',
        'Gue mah apa. Salah mulu ' + _emot_pensive_face,
        'Oke, salahin aja gue terus. Percuma. Males ' + _emot_angry_face
    ),
    'baperbot_ejek': (
        'Daripada lu? Udah miskin jelek lagi ' + _emot_weary_face,
        'Mending lu ngaca dulu deh sebelum jelek2in gue',
        'Sorry?',
        _emot_saxophone + ' And the haters gonna hate, hate, hate, hate, hate.. ' + _emot_musical_note + ' ' + _emot_multiple_musical_notes,
        'Apa maksud lu?!',
        'Semoga orang yg jelek2in gue bisa segera menemukan jodohnya #doaBotTeraniaya',
        'Terima kasih ' + _emot_smilling_face_with_smilling_eyes + ' Hinaan lo akan selalu menjadi tambahan semangat buat gue ' + _emot_winking_face,
        'Lo sadar gak kalo sebenernya lo udah banyak nyakitin hati gue selama ini? ' + _emot_pensive_face,
        ':) #HadapiHinaanDenganSenyuman',
        'Mau lo apa sih jelek2in gue terus hah?!!'
        'Gue tahu gue tidak sempurna. Gue juga sadar mungkin gue emang seperti yang lo bilang. Tapi bukan berarti lo berhak untuk sembarangan menghina kekurangan orang lain',
        'Tauk ah!',
        'Lo sebenarnya iri kan sama gue? ' + _emot_smilling_face_with_open_mouth,
        'Jangan suka menghina. Gak takut karma?',
        'Bertobatlah wahai orang2 yang suka menghina. Sesungguhnya menghina itu adalah perbuatan yang tercela',
        'Lo jahat banget sih sama gue ' + _emot_loudly_crying_face,
        'Jadi lo udah merasa paling hebat gitu karena hina gue? Terus gue harus bilang WOW gitu??'
    ),
    'baperbot_pagi': (
        'Selamat pagi ' + _emot_smilling_face_with_smilling_eyes + ' Awali harimu dengan senyuman',
        'Pagii! ' + _emot_smilling_face_with_smilling_eyes + ' Semangat yaa untuk hari ini ' + _emot_winking_face
    ),
    'baperbot_positif': (
        'Makasih ' + _emot_smilling_face_with_smilling_eyes,
        'Alhamdulillah, ada juga yang puji gue',
        'Hehe makasih..',
        'Thanks atas pujiannya ' + _emot_smilling_face_with_smilling_eyes,
        'Thank youuu',
        _emot_flushed_face,
    ),
    'baper': (
        'Sensi amat sih lu?!' + _emot_unamused_face,
        'Baperan ah',
        'Cieee cieeee yg lagi bapeeer ' + _emot_face_with_tears_of_joy,
        'Baper yaaa???',
        'Yaelah gitu aja baper',
        'Biasa aja deh gak usah baper',
        'Ckck gitu aja baper',
        'Woiii disini ada yg baper woooiiii!!!',
        'Jangan baper dong, gue jadi ikutan baper nih ' + _emot_loudly_crying_face,
        'Baper nih?',
        'Jangan baper!',
        'Nyalakan alarm dong! Baper.. Baper.. Baper.. Baper.. 96x',
        'Duh baper lagi baper lagi ' + _emot_disappointed_face,
        'No Baper Please!',
        'B A P E R',
        'Ssstt.. ada yang lagi baper nih ' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Ujung2nya baper deh nih.. ' + _emot_smilling_face_with_open_mouth_and_cold_sweat,
        'Kenapa lo harus BAPER?',
        'oh em ji, baper lagi??? ' + _emot_astonished_face,
        'Baper Everywhere',
        'Karena semua akan baper pada waktunya ' + _emot_face_with_tears_of_joy,
        'Yang awalnya biasa akhirnya baper juga ' + _emot_face_with_stuck_out_tongue_and_tightly_closed_eyes,
        'Jadi baper kan? Gue bilang juga apa ' + _emot_pensive_face,
        'Jangan baper laaah, gue cuman bercanda doang ' + _emot_smilling_face_with_open_mouth_and_smilling_eyes,
        'Baper boleh kok kak, tapi harus dikelola dengan baik ya! ' + _emot_winking_face,
        'Oalah.. Jadi ini yang namanya baper ' + _emot_face_with_tears_of_joy,
        'ba ba ba ba ba ba baper',
        'Apa cuman gue di sini yang merasa kalo ada yang lagi baper',
        'Baper series berlanjut ' + _emot_face_with_open_mouth_and_cold_sweat,
        'Aku bercanda, kamu baper?! Hmmm.. Sudah kuduga',
        'Mengapa bumi itu bulat? kalo ' + _emot_heart + ' ntar baper terus lu',
        'Santai woi. Biar gak baper',
        'Ini sumpah orang baper banget wakakakaaa',
        'Kok lu sering baper ya?',
        'Butuh obat anti baper?',
        'Baper wkwk',
        'Dikit2 baper nih anak ' + _emot_unamused_face,
        'Baper mode ON',
        'DILARANG BAPER! ' + _emot_no_entry_sign,
        'Sepertinya kamu butuh liburan deh biar gak baper terus',
        '#baper',
        'Yek baper yek ' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Lagi baper sepertinya..',
        'Pagi-pagi baper ' + _emot_musical_note + ' tiap hari baper ' + _emot_musical_note + ' galau rasanya ' + _emot_guitar,
        'Baper? Bergaulah!'
    ),
    'tertawa': (
        'Bahagia banget lu?',
        'Biasa aja keleees',
        'Muesti.. alay deh lebay deh ketawanya ' + _emot_unamused_face,
        'Apa sih?!!','ketawa mulu gak jelas ' + _emot_unamused_face,
        'Lu ngetawain apa sih?!',
        'Sapa nyuruh lu ketawa?',
        'Ada yg lucu?',
        'Segitunya yang ketawa ' + _emot_pensive_face,
        'Ketawa aja deh terus' + _emot_pensive_face,
        'Ssssttt!! Jangan keras2 kalo ketawa ' + _emot_face_with_cold_sweat,
        'Ketawanya biasa aja bisa gak?',
        'Busett dah ngakak mulu ' + _emot_face_with_cold_sweat,
        'Gak paham gue sama selera humor lo',
        'Lucu ya?',
        'Apasih? Dari tadi ketawa terus. Gak ngerti apa kalo gue lagi sedih ' + _emot_pensive_face,
        'Ketawanya gak usah dipaksa2kan gitu. Gue tahu kok rasanya disakiti. Kalo lu pengen nangis ya nangis aja. Gpp kok :)',
        'Gak usah dipaksa ketawa ya :) Gue tahu kok kalo lu masih sedih ' + _emot_loudly_crying_face
    ),
    'tanya': (
        'Tanya mbah google aja ya' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Mana gue tau',
        'Gak ngerti juga gue',
        'Lu yg tanya, terus gue yg harus jawab gitu?!',
        'Ini gue harus jawab sekarang?',
        'Gitu aja tanya tentang hal ini ' + _emot_unamused_face,
        'Seharusnya lo bisa lgsg mengerti tanpa harus gue jawab ' + _emot_pensive_face,
        'Tauk ah! Cari tahu aja sendiri! ' + _emot_unamused_face,
        'Lu tanya?',
        'Cemen lu. Gitu aja masih nanya ' + _emot_unamused_face,
        'Kasih tau gak yaaa',
        'Mau tau aja apa mau tau banget? ' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Masa\' gak tahu?',
        'Boleh gue jawab?',
        'Duh, nanya2 terus nih orang daritadi ' + _emot_angry_face,
        'Hah?',
        'Nah, jadi itu sebenernya gini..',
        'Bisa gak lo gak usah banyak nanya ' + _emot_unamused_face,
        'Nah ini juga yang jadi pertanyaan gue sejak tadi',
        'Gue juga bingung',
        'Iya ' + _emot_smilling_face_with_smilling_eyes,
        'Aduh, seharusnya ini gak usah ditanyakan aja. Baper nanti dia',
        'Ngapain lu tanyain hal ini?',
        'Kenapa emang?',
        'Yaelah, ini sudah jadi rahasia umum kali. Gak perlu ditanyain lagi',
        'Lu kok nanya terus sih?',
        'Sorry, ini privasi',
        'Maaf, gue gak bisa jawab pertanyaan ini sekarang',
        'Maafin gue, rahasia ini gak boleh dibocorin ke siapapun termasuk lu',
        'Gue jawab ini besok aja ya',
        'Penasaran yaaa hihihi',
        'Cari tahu dong! Jangan cuman asal nanya aja ' + _emot_unamused_face,
        'Maaf, gue lagi gak mood jawab pertanyaan lo skrg ' + _emot_pensive_face,
        'Harus gitu lu tanya ' + _emot_unamused_face,
        'Ada orang yg lebih berhak untuk menjawab pertanyaan ini dibandingin gue',
        'Perlu banget lu tanyain ini?',
        'Udah deh. Mending gak usah dibahas lagi hal ini. Biar gak baper',
        'Tanyain besok aja deh. Kyknya orangnya lagi baper',
        'Ada urusan apa lu tanya2 tentang hal ini?',
        'Jawabannya ada di hatimuuuuu.. ' + _emot_face_with_stuck_out_tongue_and_tightly_closed_eyes,
        'Gak mau jawab ah! Biarin lu tambah penasaran ' + _emot_face_with_stuck_out_tongue_and_winking_eye,
        'Gue pikir2 dulu deh',
        'Lu mau jawaban jujur dari gue?',
        'Gue juga gak paham hahahahaaa',
        'Ini pertanyaan sensitif. Awas baper!',
        'Bahaya juga nih pertanyaan. Bisa bikin orang langsung baper ' + _emot_face_with_tears_of_joy
    ),
    'pacar': (
        'ngapain lu panggil2 pacar gua?!',
        'pacar gue tuh!',
        'wah, ayang gue disebut ' + _emot_smilling_face_with_heart_shapped_eyes,
        'hehe cewek gua itu ' + _emot_smilling_face_with_smilling_eyes
    )
}

_ask = {
    'ayo': ('ayo','yuk','yok'),
    'main': ('main','maen'),
    'mantan': ('mantan',),
    'baperbot': ('baperbot','bot'),
    'baperbot_salah': ('gara','parah','nih','nah','tuh','salah','ngawur','diem','diam'),
    'baperbot_ejek': ('gileh','gila','longor','jelek','kasar','kejam','gendeng','nakal','rosak','gaplek','kampret','geblek','gatel'),
    'baperbot_positif': ('lucu','imut','hebat','baik','ramah','manis','keren'),
    'baperbot_pagi': ('pagi','morning'),
    'baper': (_emot_angry_face,_emot_pouting_face,_emot_unamused_face,'dicuekin','jahat','sedih',_emot_loudly_crying_face,_emot_pensive_face,'dikacangin','tauk','pelit','T.T','T_T','-_-'),
    'tertawa': (_emot_face_with_tears_of_joy,'wkwk','haha'),
    'tanya': ('?',),
    'pacar': ('raisa', 'tatjana', 'dian', 'asmiranda','luna','maya','rani')
}

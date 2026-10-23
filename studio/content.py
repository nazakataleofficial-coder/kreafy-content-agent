"""Finite editorial seed bank, not scraped trends or invented case studies.

Each item is an original recommendation. Links support technical context, not
claims that these posts have delivered engagement, clients, revenue or results.
"""
YT = 'https://support.google.com/youtube/answer/9314486'
RETENTION = 'https://support.google.com/youtube/answer/9314415'
ORIGINAL = 'https://support.google.com/youtube/answer/1311392'
BUFFER = 'https://developers.buffer.com/guides/posts-and-scheduling.html'

# Each bilingual step contains an English and Roman Urdu recommendation.
TOPICS = [
    dict(id='diagnose-views', pillar='creator-diagnostics', goal='useful-discussion',
         headline='100 VIDEOS. VIEWS NAHI?', takeaway='Har problem ka solution alag hota hai.',
         en='Publishing 100 videos cannot identify the problem for you.',
         ur='100 videos upload kar di... phir bhi views nahi? Pehle problem pehchano.',
         steps=[('Check available impressions in YouTube Studio before changing your thumbnail.', 'YouTube Studio mein available impressions dekho; thumbnail foran change mat karo.'),
                ('If impressions exist, read CTR alongside the traffic source and title-thumbnail promise.', 'Impressions hain to CTR, traffic source aur title-thumbnail ka wada saath dekho.'),
                ('Inspect retention and the opening where that report is available.', 'Retention report available ho to opening aur drop-off dekho.'),
                ('Change one clear element and compare similar videos over a sensible period.', 'Ek clear cheez badlo aur milti-julti videos ko munasib waqt de kar compare karo.')],
         question_en='Which stage is unclear in your current analytics?', question_ur='Aapko impressions, clicks ya retention mein se kis cheez ko samajhna mushkil lagta hai?', sources=[YT, RETENTION]),
    dict(id='thumbnail-promise', pillar='creator-diagnostics', goal='useful-discussion',
         headline='CLICK KE BAAD KYA?', takeaway='Title ka wada opening mein poora karo.',
         en='A click is the start of a promise, not the end of the job.',
         ur='Thumbnail click le aaye, lekin video woh baat karti bhi hai?',
         steps=[('Write the specific promise your title makes in one sentence.', 'Title ka asal wada ek jumlay mein likho.'),
                ('Check whether the opening starts delivering that promise.', 'Dekho opening us waday par kaam shuru karti hai ya nahi.'),
                ('Remove a long introduction if it delays the useful part.', 'Lamba intro useful baat ko rok raha ho to usay chhota karo.'),
                ('Use available retention data to decide what needs a new test.', 'Available retention data se agla test choose karo.')],
         question_en='What does your latest video promise in its first sentence?', question_ur='Aapki latest video ka wada ek jumlay mein kya hai?', sources=[RETENTION]),
    dict(id='show-deliverable', pillar='agency-proof', goal='qualified-enquiry',
         headline='SERVICE NAHI. KAAM DIKHAO.', takeaway='Demo ko demo kaho. Result invent mat karo.',
         en='A service list leaves the buyer to imagine the actual deliverable.',
         ur='Sirf "AI automation service" likhne se client ko kaam samajh nahi aata.',
         steps=[('Choose one workflow and describe its input and final output.', 'Ek workflow chuno aur us ka input aur final output batao.'),
                ('Record a short demo using sample data.', 'Sample data se chhota demo record karo.'),
                ('Label it as a demo and show the failure or review step too.', 'Usay demo label karo aur failure ya review step bhi dikhao.'),
                ('State the scope and ask the buyer about their actual process.', 'Scope clear karo aur buyer se us ka actual process poocho.')],
         question_en='Which repetitive process would you want demonstrated before buying?', question_ur='Aap kis repeat honay walay kaam ka demo dekh kar service lena chahenge?', sources=[BUFFER]),
    dict(id='facebook-opening', pillar='creator-diagnostics', goal='useful-discussion',
         headline='FACEBOOK KO ALAG DEKHO.', takeaway='Reach, opening aur available retention inspect karo.',
         en='A YouTube diagnosis should not be pasted onto Facebook analytics.',
         ur='YouTube ka diagnosis Facebook par seedha copy mat karo.',
         steps=[('Start with the reach and content insights actually available on your Facebook account.', 'Apne Facebook account mein jo reach aur content insights available hain, un se shuru karo.'),
                ('Check whether the opening clearly explains why someone should keep watching.', 'Opening mein dekho viewer ko rukne ki clear wajah mil rahi hai ya nahi.'),
                ('Review retention where available and read relevant audience responses.', 'Retention available ho to dekho aur relevant audience response parho.'),
                ('Test one change to topic, clarity or storytelling; record the observation.', 'Topic, clarity ya storytelling mein ek change test karo aur observation likho.')],
         question_en='Does your opening explain the value before the introduction?', question_ur='Aapki opening pehle value batati hai ya pehle lamba intro aata hai?', sources=['https://www.facebook.com/business/help']),
    dict(id='originality', pillar='creator-diagnostics', goal='useful-discussion',
         headline='NAYA TOOL. WAHI CONTENT?', takeaway='Original value aur applicable policies review karo.',
         en='Changing the AI voice does not answer the originality question.',
         ur='AI voice badal di. Lekin viewer ko nayi value kya mili?',
         steps=[('Identify the explanation, analysis or story you are adding.', 'Pehle likho aap nayi explanation, analysis ya story kya add kar rahe hain.'),
                ('Check rights for the footage, music and other material you use.', 'Footage, music aur doosray material ke rights check karo.'),
                ('Read the current policies for the platform you are publishing on.', 'Jis platform par post karna hai uski current policies parho.'),
                ('Keep a source record; do not treat an AI edit as a monetization guarantee.', 'Sources ka record rakho; AI edit ko monetization guarantee mat samjho.')],
         question_en='What part of your video would still be yours without the AI tool?', question_ur='AI tool hata dein to aapki video mein aapki apni value kya bachegi?', sources=[ORIGINAL]),
    dict(id='website-next-step', pillar='agency-proof', goal='qualified-enquiry',
         headline='VISITOR AAYA. AB KYA?', takeaway='Ek clear next step choose karo.',
         en='Before adding another website animation, check the next step.',
         ur='Website khoobsurat hai. Visitor ko agla step samajh aata hai?',
         steps=[('Write who the page is for and which problem it addresses.', 'Likho page kis ke liye hai aur kaunsa masla solve karti hai.'),
                ('Choose one primary action such as a relevant enquiry.', 'Ek primary action chuno, jaise relevant enquiry.'),
                ('Check the page and enquiry route on a real phone.', 'Real phone par page aur enquiry ka rasta check karo.'),
                ('Record actual enquiries before claiming a conversion improvement.', 'Conversion improve honay ka claim karne se pehle actual enquiries record karo.')],
         question_en='Can a new visitor identify your next step without asking you?', question_ur='Naya visitor aap se poochay baghair next step samajh sakta hai?', sources=['https://web.dev/learn/forms/']),
    dict(id='automation-review', pillar='agency-proof', goal='qualified-enquiry',
         headline='AUTO HAI. VERIFIED HAI?', takeaway='Draft, approval aur published alag statuses hain.',
         en='A green workflow is not a verified published post.',
         ur='Workflow green ho gaya. Kya post waqai sahi account par gayi?',
         steps=[('Separate draft, approved, queued and published states.', 'Draft, approved, queued aur published status alag rakho.'),
                ('Bind approval to the exact account, caption and image.', 'Approval ko exact account, caption aur image ke saath joro.'),
                ('Store the provider post ID and check the final public URL.', 'Provider post ID save karo aur final public URL verify karo.'),
                ('Pause after an uncertain upload instead of automatically retrying.', 'Upload uncertain ho to automatically repeat karne ke bajaye pause karo.')],
         question_en='What does your current system count as success?', question_ur='Aapka system kis stage ko success kehta hai?', sources=[BUFFER]),
    dict(id='one-test', pillar='creator-diagnostics', goal='useful-discussion',
         headline='EK TEST. CLEAR LEARNING.', takeaway='Sab kuch ek saath badlo ge to seekho ge kya?',
         en='Changing everything makes the next result harder to explain.',
         ur='Title, thumbnail, topic aur intro sab badal diye. Ab farq kis se para?',
         steps=[('Write one question you want the next test to answer.', 'Agla test kis sawal ka jawab dega, pehle likho.'),
                ('Choose a change that directly addresses that question.', 'Sirf woh change chuno jo us sawal se seedha related ho.'),
                ('Compare similar content and note differences in context.', 'Milta-julta content compare karo aur context ka farq note karo.'),
                ('Keep a learning log; a small sample may remain inconclusive.', 'Learning log rakho; chhota sample inconclusive bhi reh sakta hai.')],
         question_en='What is the single question behind your next upload?', question_ur='Aapki next upload ka ek clear test kya hai?', sources=[YT]),
    dict(id='qualified-enquiry', pillar='agency-proof', goal='qualified-enquiry',
         headline='LEAD HAI YA SIRF LIKE?', takeaway='Problem, scope aur timeline samjho.',
         en='A content calendar needs an enquiry record beside it.',
         ur='Likes ka record hai. Relevant enquiries ka bhi hai?',
         steps=[('Define the buyer problem your service actually addresses.', 'Woh buyer problem define karo jis par aap actual kaam kar sakte hain.'),
                ('Ask interested buyers about the task, scope and timeline.', 'Interested buyer se task, scope aur timeline samjho.'),
                ('Record the source post when the buyer can identify it.', 'Buyer ko source post yaad ho to uska record rakho.'),
                ('Track consultations and paid work separately from reactions.', 'Consultations aur paid work ko reactions se alag track karo.')],
         question_en='What would make an enquiry relevant to your service?', question_ur='Aapki service ke liye relevant enquiry ki pehchan kya hai?', sources=['https://buffer.com/resources/social-media-roi/']),
    dict(id='repurpose', pillar='creator-diagnostics', goal='useful-discussion',
         headline='EK IDEA. CHAAR VERSIONS.', takeaway='Copy-paste nahi; context ke hisaab se likho.',
         en='Repurpose the useful idea, then rewrite the delivery.',
         ur='Ek idea chaar platforms par chalega. Caption har jagah same kyun?',
         steps=[('Keep the central lesson and factual evidence consistent.', 'Asal lesson aur factual evidence same rakho.'),
                ('Use a detailed explanation for Facebook and LinkedIn when useful.', 'Zarurat ho to Facebook aur LinkedIn par detail mein samjhao.'),
                ('Make the Instagram takeaway easy to scan and X concise.', 'Instagram takeaway scan karna asaan rakho aur X par concise likho.'),
                ('Preview every image ratio and validate the final caption length.', 'Har image ratio preview karo aur final caption ki length check karo.')],
         question_en='Which platform needs the biggest rewrite in your current process?', question_ur='Aapke content ko kis platform ke liye sab se zyada rewrite chahiye?', sources=[BUFFER]),
    dict(id='automation-scope', pillar='agency-proof', goal='qualified-enquiry',
         headline='PEHLE PROCESS. PHIR BOT.', takeaway='Input, rules, review aur failure define karo.',
         en='An automation brief should describe the exception, too.',
         ur='Bot banana hai? Pehle batao ghalat input aaye to kya hona chahiye.',
         steps=[('List the input and the output you expect.', 'Input aur expected output likho.'),
                ('Write the rules for a normal run.', 'Normal run ke rules likho.'),
                ('Define who reviews sensitive or uncertain outputs.', 'Sensitive ya uncertain output ka reviewer decide karo.'),
                ('Agree on a stop condition and a visible failure record.', 'Stop condition aur nazar aanay wala failure record tay karo.')],
         question_en='Which exception would stop your workflow today?', question_ur='Aapke workflow mein kaunsi exception par system rukna chahiye?', sources=[BUFFER]),
    dict(id='proof-without-clients', pillar='agency-proof', goal='qualified-enquiry',
         headline='NO CLIENT? BUILD A DEMO.', takeaway='Sample data. Clear scope. Honest proof.',
         en='You can demonstrate a skill before you have a client testimonial.',
         ur='Client testimonial nahi? Apna kaam demo se samjhao.',
         steps=[('Choose one realistic task and clearly label sample data.', 'Ek realistic task chuno aur sample data clear label karo.'),
                ('Show the actual working output rather than an invented success metric.', 'Invented success metric ke bajaye actual working output dikhao.'),
                ('Explain what is implemented and what remains untested.', 'Batao kya implemented hai aur kya abhi untested hai.'),
                ('Invite a relevant business to discuss its own requirements.', 'Relevant business ko uski actual requirements discuss karne ki dawat do.')],
         question_en='What working output would help you assess a service provider?', question_ur='Service provider ka kaunsa working output dekhna aapke liye useful hoga?', sources=[BUFFER]),
]


POSTER_STEPS = {
    'diagnose-views': ['Impressions dekho', 'CTR samjho', 'Opening check karo'],
    'thumbnail-promise': ['Wada clear karo', 'Opening se joro', 'Drop-off dekho'],
    'show-deliverable': ['Ek task chuno', 'Working demo dikhao', 'Scope clear rakho'],
    'facebook-opening': ['Available reach dekho', 'Opening review karo', 'Ek change test karo'],
    'originality': ['Apni value likho', 'Rights check karo', 'Policies parho'],
    'website-next-step': ['Buyer clear rakho', 'Ek CTA chuno', 'Phone par test karo'],
    'automation-review': ['Account verify karo', 'Approval record rakho', 'Final URL check karo'],
    'one-test': ['Ek sawal likho', 'Ek change chuno', 'Learning record karo'],
    'qualified-enquiry': ['Problem samjho', 'Scope poochho', 'Enquiry track karo'],
    'repurpose': ['Lesson same rakho', 'Caption rewrite karo', 'Preview check karo'],
    'automation-scope': ['Input define karo', 'Rules likho', 'Stop condition rakho'],
    'proof-without-clients': ['Sample label karo', 'Output dikhao', 'Limits clear rakho'],
}
for _topic in TOPICS:
    _topic['poster_steps'] = POSTER_STEPS[_topic['id']]


def captions(topic):
    steps = topic['steps']
    buyer = topic['goal'] == 'qualified-enquiry'
    en_cta = ('For a relevant implementation discussion, visit kreafy.online and share the task, scope and timeline.'
              if buyer else 'Save the checklist for your next review.')
    ur_cta = ('Apne business ke liye implementation discuss karni ho to kreafy.online par services dekhein; task, scope aur timeline clear rakhein.'
              if buyer else 'Agli review ke liye yeh checklist save kar lein.')
    fb = '\n\n'.join([topic['ur'], 'Kabhi agla tool dhoondhne se pehle maujooda process ko dekhna zaroori hota hai. Is review ko chaar chhotay steps mein karein:',
                           *[f'{i}. {s[1]}' for i, s in enumerate(steps, 1)],
                           'Yeh practical checks hain. Views, monetization ya sales ki guarantee nahi; apne available data aur actual observations se agla decision lein.',
                           ur_cta, topic['question_ur'], '#TheAleBuilds #CreatorEducation #Kreafy'])
    li = '\n\n'.join([topic['en'], 'Use a small, documented review before choosing another tool or increasing output.',
                           *[f'{i}. {s[0]}' for i, s in enumerate(steps, 1)],
                           'Treat this as a practical test plan. Document what changed, what you observed, and what remains uncertain. It does not promise reach, monetization or revenue.',
                           en_cta, topic['question_en'], '#ContentStrategy #AIAutomation #Kreafy'])
    ig = '\n\n'.join([topic['ur'], *[f'{i}. {s[1]}' for i, s in enumerate(steps[:3], 1)],
                           topic['question_ur'], '#TheAleBuilds #ContentCreation #CreatorTips #Kreafy'])
    # Independent copy, no automatic truncation or forced website block.
    tw = '\n\n'.join([topic['en'], steps[0][0], topic['question_en']])
    return {'facebook': fb, 'linkedin': li, 'instagram': ig, 'twitter': tw}

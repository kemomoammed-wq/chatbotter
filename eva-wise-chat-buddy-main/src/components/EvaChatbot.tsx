import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Globe, Mic, MicOff, Volume2, VolumeX, Settings, RefreshCw, Copy, Download, ChevronDown, Stethoscope, Sparkles, Link as LinkIcon, Image as ImageIcon, Upload, ExternalLink, Check, CheckCheck, Square, LogOut, Palette } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { EVA_COMPANY_DATA, CONVERSATION_DATABASE, CONVERSATION_PATTERNS } from '@/data/evaData';
import { GroqService, detectLanguage, detectTone } from '@/services/groqService';
import chatService, { YoutubeVideo } from '@/services/chatService';
import authService from '@/services/authService';
import evaLogo from '@/assets/eva-logo-official.png';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import { YoutubeCard } from '@/components/ui/YoutubeCard';

type ThemeOption = {
  id: string;
  name: string;
  className: string;
  previewColor: string;
};

const THEME_OPTIONS: ThemeOption[] = [
  { id: 'eva-default', name: 'افتراضي إيفا', className: 'theme-eva-default', previewColor: '#f43f5e' },
  { id: 'ocean', name: 'أزرق محيطي', className: 'theme-ocean', previewColor: '#0ea5e9' },
  { id: 'rose', name: 'وردي جمالي', className: 'theme-rose', previewColor: '#fb7185' },
  { id: 'emerald', name: 'أخضر زمردي', className: 'theme-emerald', previewColor: '#10b981' },
  { id: 'gold', name: 'ذهبي فاخر', className: 'theme-gold', previewColor: '#f59e0b' },
  { id: 'purple', name: 'بنفسجي ملكي', className: 'theme-purple', previewColor: '#8b5cf6' },
  { id: 'teal', name: 'تيّل هادئ', className: 'theme-teal', previewColor: '#14b8a6' },
  { id: 'amber', name: 'عنبر دافئ', className: 'theme-amber', previewColor: '#f97316' },
  { id: 'pink', name: 'بينك ناعم', className: 'theme-pink', previewColor: '#ec4899' },
  { id: 'sky', name: 'سماوي', className: 'theme-sky', previewColor: '#38bdf8' },
  { id: 'lime', name: 'ليموني', className: 'theme-lime', previewColor: '#84cc16' },
  { id: 'red', name: 'أحمر قوي', className: 'theme-red', previewColor: '#ef4444' },
  { id: 'slate', name: 'رمادي أنيق', className: 'theme-slate', previewColor: '#64748b' },
  { id: 'mint', name: 'نعناعي', className: 'theme-mint', previewColor: '#22c55e' },
  { id: 'lavender', name: 'لافندر', className: 'theme-lavender', previewColor: '#a855f7' },
];

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  language: 'ar' | 'en';
  tone?: 'formal' | 'informal';
  source?: 'eva' | 'groq' | 'backend';
  productRecommendations?: string[];
  medicalAdvice?: boolean;
  imageUrl?: string;
  imageBase64?: string;
  audioUrl?: string;
  webResults?: Array<{
    title?: string;
    url?: string;
    snippet?: string;
    description?: string;
    content?: string;
    source?: string;
  }>;
  youtubeVideo?: YoutubeVideo;
}

interface ChatbotProps {
  apiKey?: string;
}

interface SkinAnalysis {
  skinType: string;
  problems: string[];
  recommendations: string[];
  routine: string[];
}

const EvaChatbot: React.FC<ChatbotProps> = ({ apiKey = 'demo-key' }) => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState<'ar' | 'en'>('ar');
  // Auto-detect tone from user message - no manual selection needed
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [groqService] = useState(() => new GroqService(apiKey));
  const [conversationMode, setConversationMode] = useState<'smart' | 'eva-only' | 'ai-only'>('smart');
  const [skinAnalysis, setSkinAnalysis] = useState<SkinAnalysis | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [themeId, setThemeId] = useState<string>('eva-default');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  // تطبيق الثيم المختار على documentElement عن طريق كلاس CSS
  useEffect(() => {
    const root = document.documentElement;
    const allClasses = THEME_OPTIONS.map(t => t.className);
    root.classList.remove(...allClasses);
    const active = THEME_OPTIONS.find(t => t.id === themeId);
    if (active) {
      root.classList.add(active.className);
    }
  }, [themeId]);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      content: language === 'ar' 
        ? 'أهلاً وسهلاً! أنا مساعد إيفا الذكي للجمال والعناية 💄✨\n\nأنا هنا عشان أساعدك في:\n🌸 تحليل نوع بشرتك وحل مشاكلها\n💅 اختيار المنتجات المناسبة علمياً\n🧴 بناء روتين عناية مثالي\n👩‍⚕️ نصائح طبية-تجميلية آمنة\n🛍️ توصيات منتجات إيفا المناسبة\n\nاكتب أو سجل رسالة صوتية عن مشكلتك، وأنا هاحللك الوضع وأديك الحل المناسب! 😊'
        : 'Hello and welcome! I\'m Eva\'s smart beauty and care assistant 💄✨\n\nI\'m here to help you with:\n🌸 Analyzing your skin type and solving problems\n💅 Choosing scientifically suitable products\n🧴 Building the perfect care routine\n👩‍⚕️ Safe medical-cosmetic advice\n🛍️ Eva product recommendations\n\nWrite or record a voice message about your concern, and I\'ll analyze your situation and give you the right solution! 😊',
      isUser: false,
      timestamp: new Date(),
      language,
      tone: 'informal',
      source: 'eva'
    };
    setMessages([welcomeMessage]);
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Smart delay for realistic responses
  const addDelay = (baseTime: number = 1000): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, baseTime + Math.random() * 1500));
  };

  // Enhanced Eva data search with auto-detected tone
  const searchEvaData = (query: string, userLanguage: 'ar' | 'en', userTone: 'formal' | 'informal'): string | null => {
    const lowerQuery = query.toLowerCase();
    
    // Check conversation database first for exact matches
    const exactMatch = CONVERSATION_DATABASE.conversations.find(conv => 
      conv.userQuery.toLowerCase() === lowerQuery || 
      lowerQuery.includes(conv.userQuery.toLowerCase())
    );
    
    if (exactMatch && exactMatch.language === userLanguage) {
      return exactMatch.botResponse;
    }

    // Smart skin problem detection and product recommendation
    const skinProblems = {
      acne: ['حبوب', 'حب الشباب', 'بثور', 'رؤوس سوداء', 'acne', 'pimples', 'breakouts', 'blackheads'],
      dryness: ['جفاف', 'جافة', 'تشقق', 'خشونة', 'dry', 'dryness', 'rough', 'flaky'],
      oily: ['دهنية', 'زيوت', 'لمعان', 'دهون', 'oily', 'greasy', 'shiny', 'sebum'],
      sensitive: ['حساسة', 'تهيج', 'احمرار', 'حكة', 'sensitive', 'irritation', 'redness', 'itchy'],
      aging: ['تجاعيد', 'شيخوخة', 'خطوط', 'ترهل', 'wrinkles', 'aging', 'fine lines', 'sagging'],
      dark_spots: ['بقع', 'تصبغ', 'بقع داكنة', 'تلون', 'dark spots', 'pigmentation', 'melasma']
    };

    // Detect user's skin problem
    let detectedProblem = '';
    
    for (const [problem, keywords] of Object.entries(skinProblems)) {
      if (keywords.some(keyword => lowerQuery.includes(keyword))) {
        detectedProblem = problem;
        break;
      }
    }

    // Product recommendations based on detected problem
    if (detectedProblem) {
      const recommendations = {
        acne: {
          products: ['غسول إيفا اللطيف للبشرة الدهنية', 'سيرم فيتامين C المضاد للأكسدة', 'كريم علاج الحبوب'],
          arMessage: `${userTone === 'formal' ? 'أتفهم مشكلتك مع الحبوب، وهذا أمر شائع يمكن علاجه' : 'فهمت إن عندك مشكلة حبوب! 🤗 دي مشكلة شائعة وليها حل'}:\n\n💄 المنتجات المناسبة:\n• غسول إيفا اللطيف للبشرة الدهنية - 150ج\n  ▫️ يحتوي على حمض الساليسيليك 2% لتنظيف المسام\n  ▫️ الزنك PCA يقلل البكتيريا\n  ▫️ الألوة فيرا تهدئ الالتهاب\n\n• سيرم فيتامين C المضاد للأكسدة - 350ج\n  ▫️ يفتح البقع الداكنة من آثار الحبوب\n  ▫️ يحارب البكتيريا الضارة\n\n${userTone === 'formal' ? '🔄 البرنامج العلاجي الموصى به:' : '🔄 الروتين المثالي:'}\nصباحاً: غسول → سيرم → مرطب خفيف → واقي شمس\nمساءً: غسول → علاج موضعي → مرطب مهدئ\n\n⚠️ ${userTone === 'formal' ? 'إرشادات طبية مهمة:' : 'نصائح مهمة:'}\n• ${userTone === 'formal' ? 'يُنصح بعدم عصر الحبوب نهائياً' : 'لا تعصر الحبوب نهائياً'}\n• ${userTone === 'formal' ? 'يُفضل تغيير غطاء الوسادة يومياً' : 'غير غطاء الوسادة يومياً'}\n• ${userTone === 'formal' ? 'تجنب لمس منطقة الوجه' : 'تجنب لمس الوجه'}\n• ${userTone === 'formal' ? 'النتائج تظهر خلال 4-6 أسابيع' : 'النتائج تظهر بعد 4-6 أسابيع'}\n\n💬 أسئلة أخرى عن المنتجات:\n• ${userTone === 'formal' ? 'كم من الوقت أحتاج لاستخدام المنتج؟' : 'كم وقت محتاج استخدم المنتج؟'}\n• ${userTone === 'formal' ? 'هل يمكن استخدامه مع منتجات أخرى؟' : 'ممكن استخدمه مع منتجات تانية؟'}\n• ${userTone === 'formal' ? 'ما هي أفضل أوقات الاستخدام؟' : 'إيه أحسن أوقات استخدمه؟'}\n\n${userTone === 'formal' ? 'هل تود معرفة المزيد عن منتج محدد؟' : 'عايز تعرف أكتر عن منتج معين؟'}`,
          enMessage: `${userTone === 'formal' ? 'I understand your acne concerns. This is a common condition that can be effectively treated' : 'I understand you have acne concerns! 🤗 This is common and treatable'}:\n\n💄 Recommended Products:\n• Eva Gentle Facial Cleanser for Oily Skin - 150 EGP\n  ▫️ Contains 2% Salicylic Acid for pore cleansing\n  ▫️ Zinc PCA reduces bacteria\n  ▫️ Aloe Vera soothes inflammation\n\n• Vitamin C Antioxidant Serum - 350 EGP\n  ▫️ Brightens dark spots from acne marks\n  ▫️ Fights harmful bacteria\n\n${userTone === 'formal' ? '🔄 Recommended Treatment Protocol:' : '🔄 Perfect Routine:'}\nMorning: Cleanser → Serum → Light moisturizer → Sunscreen\nEvening: Cleanser → Spot treatment → Soothing moisturizer\n\n⚠️ ${userTone === 'formal' ? 'Important Medical Guidelines:' : 'Important Tips:'}\n• ${userTone === 'formal' ? 'It is strongly advised not to squeeze pimples' : 'Never squeeze pimples'}\n• ${userTone === 'formal' ? 'Daily pillowcase changes are recommended' : 'Change pillowcase daily'}\n• ${userTone === 'formal' ? 'Avoid touching the facial area' : 'Avoid touching face'}\n• ${userTone === 'formal' ? 'Results typically appear within 4-6 weeks' : 'Results show after 4-6 weeks'}\n\n💬 More product questions:\n• ${userTone === 'formal' ? 'How long should I use this product?' : 'How long to use this product?'}\n• ${userTone === 'formal' ? 'Can it be used with other products?' : 'Can I use it with other products?'}\n• ${userTone === 'formal' ? 'What are the best application times?' : 'Best times to use it?'}\n\n${userTone === 'formal' ? 'Would you like to know more about a specific product?' : 'Want to know more about a specific product?'}`
        },
        dryness: {
          products: ['مرطب إيفا المائي للبشرة الجافة', 'مقشر إيفا اللطيف للبشرة الحساسة'],
          arMessage: `${userTone === 'formal' ? 'ألاحظ أن بشرتك تعاني من الجفاف، وهذا أمر قابل للعلاج بالمنتجات المناسبة' : 'أشوف إن بشرتك جافة! 💧 مش مشكلة، إيفا عندها الحل السحري'}:\n\n💄 المنتجات المناسبة:\n• مرطب إيفا المائي للبشرة الجافة - 220ج\n  ▫️ حمض الهيالورونيك يحتفظ بالرطوبة 48 ساعة\n  ▫️ نياسيناميد 5% يقوي حاجز البشرة\n  ▫️ السيراميدز تمنع فقدان الماء\n\n• مقشر إيفا اللطيف للبشرة الحساسة - 180ج\n  ▫️ أحماض فواكه طبيعية تزيل الجلد الميت\n  ▫️ الشوفان والعسل يرطبان بعمق\n\n${userTone === 'formal' ? '🔄 البرنامج العلاجي الموصى به:' : '🔄 الروتين السحري:'}\nصباحاً: غسول لطيف → سيرم مرطب → مرطب غني → واقي شمس\nمساءً: زيت منظف → سيرم → كريم ليلي مكثف\nأسبوعياً: مقشر لطيف مرة واحدة\n\n💬 أسئلة شائعة عن المنتجات:\n• ${userTone === 'formal' ? 'هل يناسب جميع أنواع البشرة؟' : 'ده يناسب كل أنواع البشرة؟'}\n• ${userTone === 'formal' ? 'كم مرة في اليوم أستخدمه؟' : 'كم مرة في اليوم استخدمه؟'}\n• ${userTone === 'formal' ? 'هل له رائحة مميزة؟' : 'له ريحة حلوة؟'}\n\n${userTone === 'formal' ? 'هل تود معرفة المزيد؟' : 'عايز تعرف أكتر؟ 😊'}`,
          enMessage: `${userTone === 'formal' ? 'I observe that your skin is experiencing dryness, which can be treated with appropriate products' : 'I see your skin is dry! 💧 No worries, Eva has the magical solution'}:\n\n💄 Recommended Products:\n• Eva Hydrating Moisturizer for Dry Skin - 220 EGP\n  ▫️ Hyaluronic Acid retains moisture for 48 hours\n  ▫️ 5% Niacinamide strengthens skin barrier\n  ▫️ Ceramides prevent water loss\n\n• Eva Gentle Exfoliating Scrub - 180 EGP\n  ▫️ Natural fruit acids remove dead skin\n  ▫️ Oats and honey deeply moisturize\n\n${userTone === 'formal' ? '🔄 Recommended Treatment Protocol:' : '🔄 Magic Routine:'}\nMorning: Gentle cleanser → Hydrating serum → Rich moisturizer → Sunscreen\nEvening: Oil cleanser → Serum → Intensive night cream\nWeekly: Gentle scrub once\n\n💬 Common product questions:\n• ${userTone === 'formal' ? 'Does it suit all skin types?' : 'Good for all skin types?'}\n• ${userTone === 'formal' ? 'How many times per day should I use it?' : 'How many times daily?'}\n• ${userTone === 'formal' ? 'Does it have a distinctive fragrance?' : 'Does it smell nice?'}\n\n${userTone === 'formal' ? 'Would you like to know more?' : 'Want to know more? 😊'}`
        },
        oily: {
          products: ['غسول إيفا اللطيف للبشرة الدهنية', 'واقي الشمس إيفا SPF 50+'],
          arMessage: `${userTone === 'formal' ? 'البشرة الدهنية لها مميزات عديدة عند العناية الصحيحة بها' : 'بشرتك دهنية؟ 🌟 ده مش عيب، ده نعمة لو عرفتِ تتعاملي معاها صح! أنا هنا عشان أساعدك'}:\n\n💄 المنتجات المناسبة:\n• غسول إيفا اللطيف للبشرة الدهنية - 150ج\n  ▫️ ينظف الزيوت الزائدة بدون جفاف\n  ▫️ حمض الساليسيليك ينظف المسام بعمق\n\n• واقي الشمس إيفا SPF 50+ - 280ج\n  ▫️ تركيبة خفيفة غير دهنية\n  ▫️ مقاوم للماء والعرق\n  ▫️ لا يسد المسام\n\n💬 أسئلة مهمة عن المنتجات:\n• ${userTone === 'formal' ? 'هل يقلل من إفراز الزيوت؟' : 'ده هيقلل الزيوت الزايدة؟'}\n• ${userTone === 'formal' ? 'متى تظهر النتائج؟' : 'هاشوف نتيجة امتى؟'}\n• ${userTone === 'formal' ? 'هل يمكن استخدامه صباحاً ومساءً؟' : 'أقدر استخدمه الصبح والمغرب؟'}\n• ${userTone === 'formal' ? 'هل مناسب للبشرة الحساسة؟' : 'مناسب للبشرة الحساسة؟'}\n\n${userTone === 'formal' ? 'هل تريد معرفة تفاصيل أكثر عن منتج محدد؟' : 'عايز تعرف أكتر عن منتج معين؟ 😊'}`,
          enMessage: `${userTone === 'formal' ? 'Oily skin has many advantages when properly cared for' : 'Oily skin? 🌟 That\'s not a flaw, it\'s a blessing if you handle it right! I\'m here to help'}:\n\n💄 Recommended Products:\n• Eva Gentle Cleanser for Oily Skin - 150 EGP\n  ▫️ Removes excess oil without drying\n  ▫️ Salicylic acid deep cleans pores\n\n• Eva Sunscreen SPF 50+ - 280 EGP\n  ▫️ Lightweight non-greasy formula\n  ▫️ Water and sweat resistant\n  ▫️ Non-comedogenic\n\n💬 Important product questions:\n• ${userTone === 'formal' ? 'Does it reduce oil production?' : 'Will it reduce excess oil?'}\n• ${userTone === 'formal' ? 'When will results appear?' : 'When will I see results?'}\n• ${userTone === 'formal' ? 'Can it be used morning and evening?' : 'Can I use it AM and PM?'}\n• ${userTone === 'formal' ? 'Is it suitable for sensitive skin?' : 'Good for sensitive skin?'}\n\n${userTone === 'formal' ? 'Would you like to know more details about a specific product?' : 'Want to know more about a specific product? 😊'}`
        }
      };

      const recommendation = recommendations[detectedProblem as keyof typeof recommendations];
      if (recommendation) {
        return userLanguage === 'ar' ? recommendation.arMessage : recommendation.enMessage;
      }
    }

    // Hair care queries detection (منتجات للشعر، تنعيم الشعر، etc.)
    const hairKeywords = [
      'شعر', 'hair', 'شامبو', 'shampoo', 'بلسم', 'conditioner', 'ماسك', 'mask',
      'تنعيم', 'soften', 'تلف', 'damage', 'تقصف', 'split', 'جفاف', 'dry hair',
      'haircare', 'hair care', 'عناية بالشعر', 'للشعر', 'لشعري'
    ];
    
    const hasHairQuery = hairKeywords.some(keyword => lowerQuery.includes(keyword));
    
    if (hasHairQuery) {
      // User asked about hair products
      const greeting = userTone === 'formal' 
        ? (userLanguage === 'ar' ? 'أهلاً بك! سأساعدك في اختيار منتجات الشعر المناسبة' : 'Welcome! I\'ll help you choose the right hair products')
        : (userLanguage === 'ar' ? 'أهلاً! 🌟 أنا هنا عشان أساعدك في اختيار منتجات الشعر المناسبة لشعرك' : 'Hey there! 🌟 I\'m here to help you choose the right hair products');
      
      const productsIntro = userTone === 'formal'
        ? (userLanguage === 'ar' ? 'منتجات إيفا المميزة للعناية بالشعر:' : 'Eva\'s outstanding haircare products:')
        : (userLanguage === 'ar' ? 'إيفا عندها تشكيلة رائعة من منتجات العناية بالشعر:' : 'Eva has an amazing range of haircare products:');
      
      if (userLanguage === 'ar') {
        return `${greeting}:\n\n💇‍♀️ ${productsIntro}\n\n• شامبو ألو إيفا المرطب (كود 101) - 120ج\n  ▫️ للشعر الجاف والمتضرر والمعالج كيميائياً\n  ▫️ ترطيب عميق وإصلاح التلف\n  ▫️ لمعان طبيعي\n\n• ماسك إيفا هير كلينك للإصلاح المكثف (كود 102) - 200ج\n  ▫️ للشعر التالف والمصبوغ والمتقصف\n  ▫️ إصلاح عميق وتقوية البصيلات\n  ▫️ يمنع التقصف\n\n• بلسم إيفا للشعر الجاف (كود 103) - 150ج\n  ▫️ ترطيب فوري وسهولة في التمشيط\n  ▫️ يحمي من الحرارة\n\n💡 ${userTone === 'formal' ? 'لتقديم توصية أدق، يرجى إخباري:' : 'عشان أقدر أوصيك بالمنتج المناسب، قولي:'}\n• نوع شعرك (جاف، دهني، عادي، تالف)\n• المشكلة اللي عندك (تقصف، جفاف، تلف من الصبغة)\n• هدفك (تنعيم، ترطيب، إصلاح)\n\n${userTone === 'formal' ? 'مثال: "شعري جاف ومتقصف" أو "شعري تالف من الصبغة"' : 'مثال: "شعري جاف ومتقصف" أو "شعري تالف من الصبغة"'} 😊`;
      } else {
        return `${greeting}:\n\n💇‍♀️ ${productsIntro}\n\n• Aloe Eva Hydrating Shampoo (code 101) - 120 EGP\n  ▫️ For dry, damaged, and chemically treated hair\n  ▫️ Deep hydration and damage repair\n  ▫️ Natural shine\n\n• Eva Hair Clinic Intensive Repair Mask (code 102) - 200 EGP\n  ▫️ For damaged, colored, and split hair\n  ▫️ Deep repair and follicle strengthening\n  ▫️ Prevents split ends\n\n• Eva Conditioner for Dry Hair (code 103) - 150 EGP\n  ▫️ Instant hydration and easy combing\n  ▫️ Heat protection\n\n💡 ${userTone === 'formal' ? 'For a more accurate recommendation, please tell me:' : 'To recommend the right product, tell me:'}\n• Your hair type (dry, oily, normal, damaged)\n• The problem you have (split ends, dryness, damage from coloring)\n• Your goal (softening, hydration, repair)\n\n${userTone === 'formal' ? 'Example: "My hair is dry and split" or "My hair is damaged from coloring"' : 'Example: "My hair is dry and split" or "My hair is damaged from coloring"'} 😊`;
      }
    }

    // General skin care queries detection (محتاج حاجه للبشره, etc.)
    const generalSkinKeywords = [
      'محتاج', 'حاجه', 'للجلد', 'للبشره', 'بشره', 'جلد', 'منتج', 'منتجات',
      'skin', 'skincare', 'need', 'product', 'products', 'for skin', 'skin care'
    ];
    
    const hasGeneralSkinQuery = generalSkinKeywords.some(keyword => lowerQuery.includes(keyword)) &&
      (lowerQuery.includes('بشره') || lowerQuery.includes('جلد') || lowerQuery.includes('skin'));
    
    if (hasGeneralSkinQuery && !detectedProblem) {
      // User asked for general skin care products but didn't specify a problem
      const greeting = userTone === 'formal' 
        ? (userLanguage === 'ar' ? 'أهلاً بك! سأساعدك في اختيار المنتجات المناسبة لبشرتك' : 'Welcome! I\'ll help you choose the right products for your skin')
        : (userLanguage === 'ar' ? 'أهلاً! 🎯 أنا هنا عشان أساعدك في اختيار المنتجات المناسبة لبشرتك' : 'Hey there! 🎯 I\'m here to help you choose the right products for your skin');
      
      const productsIntro = userTone === 'formal'
        ? (userLanguage === 'ar' ? 'منتجات إيفا المميزة للعناية بالبشرة:' : 'Eva\'s outstanding skincare products:')
        : (userLanguage === 'ar' ? 'إيفا عندها تشكيلة رائعة من منتجات العناية بالبشرة:' : 'Eva has an amazing range of skincare products:');
      
      const askForDetails = userTone === 'formal'
        ? (userLanguage === 'ar' ? '🔍 لتقديم توصية أدق، يرجى إخباري:' : '🔍 For a more accurate recommendation, please tell me:')
        : (userLanguage === 'ar' ? '🔍 عشان أقدر أوصيك بالمنتج المناسب، قولي:' : '🔍 To recommend the right product, tell me:');
      
      const skinType = userLanguage === 'ar' ? 'نوع بشرتك (دهنية، جافة، عادية، حساسة)' : 'Your skin type (oily, dry, normal, sensitive)';
      const problem = userTone === 'formal'
        ? (userLanguage === 'ar' ? 'المشكلة التي تواجهها (حبوب، جفاف، بقع، تجاعيد)' : 'The problem you face (acne, dryness, spots, wrinkles)')
        : (userLanguage === 'ar' ? 'المشكلة اللي عندك (حبوب، جفاف، بقع، تجاعيد)' : 'The problem you have (acne, dryness, spots, wrinkles)');
      const goal = userTone === 'formal'
        ? (userLanguage === 'ar' ? 'الهدف من الاستخدام (ترطيب، علاج، حماية)' : 'Your usage goal (hydration, treatment, protection)')
        : (userLanguage === 'ar' ? 'هدفك من الاستخدام (ترطيب، علاج، حماية)' : 'Your goal (hydration, treatment, protection)');
      
      const example = userTone === 'formal'
        ? (userLanguage === 'ar' ? 'مثال: "بشرتي دهنية وعندي حبوب" أو "بشرتي جافة ومحتاجة ترطيب"' : 'Example: "My skin is oily and I have acne" or "My skin is dry and needs hydration"')
        : (userLanguage === 'ar' ? 'مثال: "بشرتي دهنية وعندي حبوب" أو "بشرتي جافة ومحتاجة ترطيب"' : 'Example: "My skin is oily and I have acne" or "My skin is dry and needs hydration"');
      
      if (userLanguage === 'ar') {
        return `${greeting}:\n\n💄 ${productsIntro}\n\n• غسول إيفا اللطيف للبشرة الدهنية (كود 001) - 150ج\n  ▫️ للبشرة الدهنية والمعرضة للحبوب\n\n• مرطب إيفا المائي للبشرة الجافة (كود 002) - 220ج\n  ▫️ للبشرة الجافة والحساسة\n\n• واقي الشمس إيفا SPF 50+ (كود 003) - 280ج\n  ▫️ حماية من أشعة الشمس الضارة\n\n• سيرم فيتامين C المضاد للأكسدة (كود 004) - 350ج\n  ▫️ لإشراقة البشرة وتوحيد اللون\n\n• مقشر إيفا اللطيف (كود 005) - 180ج\n  ▫️ لإزالة الخلايا الميتة\n\n${askForDetails}\n• ${skinType}\n• ${problem}\n• ${goal}\n\n${example} 😊`;
      } else {
        return `${greeting}:\n\n💄 ${productsIntro}\n\n• Eva Gentle Cleanser for Oily Skin (code 001) - 150 EGP\n  ▫️ For oily and acne-prone skin\n\n• Eva Hydrating Moisturizer for Dry Skin (code 002) - 220 EGP\n  ▫️ For dry and sensitive skin\n\n• Eva Sunscreen SPF 50+ (code 003) - 280 EGP\n  ▫️ Protection from harmful sun rays\n\n• Vitamin C Antioxidant Serum (code 004) - 350 EGP\n  ▫️ For skin radiance and tone evenness\n\n• Eva Gentle Exfoliator (code 005) - 180 EGP\n  ▫️ For removing dead cells\n\n${askForDetails}\n• ${skinType}\n• ${problem}\n• ${goal}\n\n${example} 😊`;
      }
    }

    // Enhanced greetings with emotional warmth
    if (lowerQuery.includes('hello') || lowerQuery.includes('hi') || lowerQuery.includes('أهلا') ||
        lowerQuery.includes('مرحبا') || lowerQuery.includes('السلام') || lowerQuery.includes('صباح') ||
        lowerQuery.includes('مساء') || lowerQuery.includes('إزيك') || lowerQuery.includes('ازيك') ||
        lowerQuery.includes('ازاي') || lowerQuery.includes('عامل') || lowerQuery.includes('اخبارك')) {
      return userLanguage === 'ar'
        ? `أهلاً وسهلاً وأهلاً تاني! 🌟✨ أنا مساعد إيفا الذكي، وفرحانة جداً إني أتكلم معاك!\n\n${userTone === 'formal' ? 'كيف يمكنني مساعدتك اليوم؟' : 'إزاي أقدر أساعدك النهاردة؟'} 😊\n\n💄 أقدر أساعدك في:\n• تحليل نوع بشرتك وحل مشاكلها 🔍\n• اختيار المنتجات المناسبة ليك 🎯\n• بناء روتين عناية مثالي ✨\n• نصائح جمالية وطبية آمنة 👩‍⚕️\n• توصيات منتجات إيفا الرائعة 🛍️\n\n${userTone === 'formal' ? 'أرجو منك وصف مشكلتك أو استفسارك' : 'قولي مشكلتك أو أي حاجة عايزة تعرفيها'} وأنا هاديك أفضل حل! 💕`
        : `Hello and warmest welcome! 🌟✨ I'm Eva's smart assistant, and I'm absolutely delighted to talk with you!\n\n${userTone === 'formal' ? 'How may I assist you today?' : 'How can I help you today?'} 😊\n\n💄 I can help you with:\n• Analyzing your skin type and solving problems 🔍\n• Choosing the right products for you 🎯\n• Building the perfect care routine ✨\n• Safe beauty and medical advice 👩‍⚕️\n• Amazing Eva product recommendations 🛍️\n\n${userTone === 'formal' ? 'Please describe your concern or inquiry' : 'Tell me your concern or anything you\'d like to know'} and I'll give you the best solution! 💕`;
    }

    return null; // Return null if no match found, will trigger AI response
  };

  // Enhanced message sending with realistic delay
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      isUser: true,
      timestamp: new Date(),
      language: detectLanguage(inputValue),
      tone: detectTone(inputValue, detectLanguage(inputValue)),
      source: 'eva'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Add realistic thinking delay
    await addDelay(800);

    try {
      // Update detected language and tone
      const detectedLang = detectLanguage(inputValue);
      const detectedToneValue = detectTone(inputValue, detectedLang);
      setLanguage(detectedLang);

      // Always use backend API first - يستمد البيانات من الإنترنت مباشرة
      let botResponse: string | null = null;
      let source: 'eva' | 'groq' | 'backend' = 'backend';
      let webResults: any[] = [];
      
      await addDelay(800); // Delay for thinking
      
      // Try backend API first - يستمد البيانات من الإنترنت واللينكات
      try {
        const backendResponse = await chatService.sendMessage({
          message: inputValue.trim(),
          user_id: getUserId(), // Use username from login
          language: detectedLang,
          conversation_mode: conversationMode,
        });
        
        if (backendResponse.success && backendResponse.response) {
          botResponse = backendResponse.response;
          source = 'backend';
          // Store web results for later use
          if (backendResponse.web_results) {
            webResults = backendResponse.web_results;
          }
        } else {
          throw new Error('Backend response failed');
        }
      } catch (backendError) {
        // Fallback: Try local data only if backend fails
        botResponse = searchEvaData(inputValue.trim(), detectedLang, detectedToneValue);
        source = 'eva';
        
        // If still no response, use AI
        if (!botResponse) {
          try {
            await addDelay(1200);
            const aiResponse = await groqService.generateResponse(
              inputValue.trim(),
              detectedLang,
              detectedToneValue,
              'Eva beauty assistant - search the web for current information'
            );
            
            botResponse = aiResponse || (detectedLang === 'ar' 
              ? `شكراً لسؤالك! 🤗 أنا أبحث في الإنترنت للحصول على أحدث المعلومات. ممكن توضحلي أكتر عشان أقدر أساعدك بشكل أدق؟`
              : `Thank you for your question! 🤗 I'm searching the web for the latest information. Could you clarify more so I can help you more accurately?`);
            source = 'groq';
          } catch (error) {
            // Final fallback
            botResponse = detectedLang === 'ar'
              ? `أهلاً بيك! 🌟 أنا أبحث في الإنترنت للحصول على معلومات محدثة. عايز تسأل عن إيه تحديداً؟`
              : `Welcome! 🌟 I'm searching the web for updated information. What specifically would you like to ask about?`;
            source = 'eva';
          }
        }
      }

      // Final delay before showing response
      await addDelay(600);

      // لو فيه فيديو شرح مرفق من الباك اند، وضّح للمستخدم في النص
      if (backendResponse.youtube_video) {
        if (detectedLang === 'ar') {
          botResponse += '\n\n🎥 لقيت لك فيديو شرح مناسب فوق، اضغط على الكارت وهيفتح معاك في يوتيوب.';
        } else {
          botResponse += '\n\n🎥 I found a helpful YouTube video above. Click the card to open it on YouTube.';
        }
      }

      const responseMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: botResponse,
        isUser: false,
        timestamp: new Date(),
        language: detectedLang,
        tone: detectedToneValue,
        source,
        webResults: webResults,
        youtubeVideo: backendResponse && backendResponse.youtube_video ? backendResponse.youtube_video : undefined
      };

      setMessages(prev => [...prev, responseMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: language === 'ar' 
          ? 'عذراً، حدث خطأ تقني. ممكن تحاول تاني؟ 🤖'
          : 'Sorry, a technical error occurred. Could you try again? 🤖',
        isUser: false,
        timestamp: new Date(),
        language,
        tone: 'informal',
        source: 'eva'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };


  // Copy message to clipboard
  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    toast({
      title: language === 'ar' ? 'تم النسخ' : 'Copied',
      description: language === 'ar' ? 'تم نسخ الرسالة' : 'Message copied to clipboard'
    });
  };

  // Export conversation
  const exportConversation = () => {
    const conversation = messages.map(msg => 
      `${msg.isUser ? (language === 'ar' ? 'أنت' : 'You') : 'Eva'} (${msg.timestamp.toLocaleString()}): ${msg.content}`
    ).join('\n\n');
    
    const blob = new Blob([conversation], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eva-conversation-${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: language === 'ar' ? 'تم التصدير' : 'Exported',
      description: language === 'ar' ? 'تم تصدير المحادثة بنجاح' : 'Conversation exported successfully'
    });
  };

  // Clear conversation
  const clearConversation = () => {
    setMessages([]);
    setTimeout(() => {
      const welcomeMessage: Message = {
        id: '1',
        content: language === 'ar' 
          ? 'تم مسح المحادثة! 🔄 كيف يمكنني مساعدتك اليوم؟'
          : 'Conversation cleared! 🔄 How can I help you today?',
        isUser: false,
        timestamp: new Date(),
        language,
        tone: 'informal',
        source: 'eva'
      };
      setMessages([welcomeMessage]);
    }, 100);
  };

  // Speech Recognition - Hybrid: Browser API + Backend
  useEffect(() => {
    // Try browser API first (faster, but may not work offline)
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = language === 'ar' ? 'ar-SA' : 'en-US';

      recognitionRef.current.onresult = async (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
        toast({
          title: language === 'ar' ? 'تم التعرف على الصوت' : 'Speech Recognized',
          description: transcript
        });
        // Auto-send if text is detected - will be handled by user clicking send or Enter
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        // Fallback to recording if browser API fails
        if (event.error === 'not-allowed' || event.error === 'no-speech') {
          startAudioRecording();
        } else {
          toast({
            title: language === 'ar' ? 'خطأ في التعرف على الصوت' : 'Speech Recognition Error',
            description: event.error,
            variant: 'destructive'
          });
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    synthRef.current = window.speechSynthesis;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (synthRef.current) {
        synthRef.current.cancel();
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, [language, toast]);

  // Audio Recording for Backend Speech-to-Text
  const startAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        stream.getTracks().forEach(track => track.stop());
        
        // Send to backend
        setIsLoading(true);
        try {
          const result = await chatService.speechToText(audioBlob, language);
          if (result.success && result.text) {
            setInputValue(result.text);
            toast({
              title: language === 'ar' ? 'تم التعرف على الصوت' : 'Speech Recognized',
              description: result.text
            });
            // Text is now in input field - user can press Enter to send
          } else {
            throw new Error(result.error || 'Recognition failed');
          }
        } catch (error) {
          console.error('Backend speech-to-text error:', error);
          toast({
            title: language === 'ar' ? 'خطأ في التعرف على الصوت' : 'Speech Recognition Error',
            description: error instanceof Error ? error.message : 'Unknown error',
            variant: 'destructive'
          });
        } finally {
          setIsLoading(false);
          setIsRecording(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast({
        title: language === 'ar' ? 'جاري التسجيل...' : 'Recording...',
        description: language === 'ar' ? 'تحدث الآن' : 'Speak now'
      });
    } catch (error) {
      console.error('Error starting audio recording:', error);
      toast({
        title: language === 'ar' ? 'خطأ في الوصول للميكروفون' : 'Microphone Access Error',
        description: error instanceof Error ? error.message : 'Please allow microphone access',
        variant: 'destructive'
      });
      setIsRecording(false);
    }
  };

  const stopAudioRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const toggleSpeechRecognition = () => {
    if (isListening || isRecording) {
      // Stop current recognition/recording
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (mediaRecorderRef.current) {
        stopAudioRecording();
      }
      setIsListening(false);
      setIsRecording(false);
      return;
    }

    // Try browser API first
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        toast({
          title: language === 'ar' ? 'جاري الاستماع...' : 'Listening...',
          description: language === 'ar' ? 'تحدث الآن' : 'Speak now'
        });
      } catch (error) {
        console.error('Error starting recognition:', error);
        // Fallback to audio recording
        startAudioRecording();
      }
    } else {
      // Use audio recording (works with backend)
      startAudioRecording();
    }
  };

  // Text to Speech - Hybrid: Browser API + Backend
  const toggleTextToSpeech = async () => {
    if (isSpeaking) {
      // Stop current speech
      if (synthRef.current) {
        synthRef.current.cancel();
      }
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      setIsSpeaking(false);
      return;
    }

    // Get last bot message
    const lastBotMessage = [...messages].reverse().find(msg => !msg.isUser);
    if (!lastBotMessage) {
      toast({
        title: language === 'ar' ? 'لا توجد رسالة للقراءة' : 'No message to read',
        description: language === 'ar' ? 'لا توجد رسالة من البوت للقراءة' : 'No bot message to read'
      });
      return;
    }

    setIsSpeaking(true);

    // Try backend first (better quality, especially for Arabic)
    try {
      const result = await chatService.textToSpeech(lastBotMessage.content, lastBotMessage.language);
      if (result.success && result.audioUrl) {
        // Play audio from backend
        const audio = new Audio(result.audioUrl);
        audioPlayerRef.current = audio;
        
        audio.onended = () => {
          setIsSpeaking(false);
          URL.revokeObjectURL(result.audioUrl!);
        };

        audio.onerror = () => {
          setIsSpeaking(false);
          // Fallback to browser API
          useBrowserTTS(lastBotMessage);
        };

        audio.play();
        toast({
          title: language === 'ar' ? 'جاري القراءة...' : 'Reading...',
          description: language === 'ar' ? 'من الخادم' : 'From server'
        });
      } else {
        throw new Error('Backend TTS failed');
      }
    } catch (error) {
      console.error('Backend TTS error, using browser API:', error);
      // Fallback to browser API
      useBrowserTTS(lastBotMessage);
    }
  };

  const useBrowserTTS = (message: Message) => {
    if (!synthRef.current) {
      toast({
        title: language === 'ar' ? 'غير مدعوم' : 'Not Supported',
        description: language === 'ar' ? 'المتصفح لا يدعم تحويل النص إلى صوت' : 'Browser does not support text to speech',
        variant: 'destructive'
      });
      setIsSpeaking(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(message.content);
    utterance.lang = message.language === 'ar' ? 'ar-SA' : 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      toast({
        title: language === 'ar' ? 'خطأ في تحويل النص إلى صوت' : 'Text to Speech Error',
        variant: 'destructive'
      });
    };

    synthRef.current.speak(utterance);
  };

  // Image Upload Handler
  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'الملف المحدد ليس صورة' : 'Selected file is not an image',
        variant: 'destructive'
      });
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: language === 'ar' ? 'خطأ' : 'Error',
        description: language === 'ar' ? 'حجم الصورة كبير جداً (الحد الأقصى 10MB)' : 'Image size is too large (max 10MB)',
        variant: 'destructive'
      });
      return;
    }

    try {
      // Show loading
      setIsLoading(true);

      // Upload to backend
      const result = await chatService.uploadImage(file);

      if (result.success && result.data) {
        // Create user message with image
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64String = reader.result as string;
          
          const userMessage: Message = {
            id: Date.now().toString(),
            content: language === 'ar' ? '📷 صورة مرفوعة' : '📷 Image uploaded',
            isUser: true,
            timestamp: new Date(),
            language,
            tone: 'informal',
            source: 'eva',
            imageBase64: base64String,
            imageUrl: result.data?.filepath
          };

          setMessages(prev => [...prev, userMessage]);

          // Process image with chatbot
          handleImageMessage(file, base64String);
        };
        reader.readAsDataURL(file);
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      toast({
        title: language === 'ar' ? 'خطأ في رفع الصورة' : 'Image Upload Error',
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Handle image message processing
  const handleImageMessage = async (file: File, base64String: string) => {
    try {
      // Add delay for processing
      await addDelay(1000);

      // Create bot response about the image
      const detectedLang = language;
      const imageInfo = `📷 ${language === 'ar' ? 'تم رفع صورة' : 'Image uploaded'}: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: detectedLang === 'ar'
          ? `شكراً لرفع الصورة! 📷\n\nأنا أعالج الصورة الآن...\n\n${imageInfo}\n\n💡 ${detectedLang === 'ar' ? 'يمكنك وصف ما تريد معرفته عن الصورة' : 'You can describe what you want to know about the image'}`
          : `Thank you for uploading the image! 📷\n\nI'm processing the image now...\n\n${imageInfo}\n\n💡 ${detectedLang === 'ar' ? 'يمكنك وصف ما تريد معرفته عن الصورة' : 'You can describe what you want to know about the image'}`,
        isUser: false,
        timestamp: new Date(),
        language: detectedLang,
        tone: 'informal',
        source: 'backend'
      };

      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Error processing image message:', error);
    }
  };

  // Main component render
  return (
    <div className="flex flex-col h-screen bg-[#f7f7f8] dark:bg-[#343541]">
      {/* Header - ChatGPT Style */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-[#343541] px-4 py-3 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#ab68ff] flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {language === 'ar' ? 'Eva' : 'Eva'}
              </h1>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearConversation}
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 h-8 px-2"
              title={language === 'ar' ? 'محادثة جديدة' : 'New Chat'}
            >
              <RefreshCw className="w-4 h-4" />
            </Button>

            {/* Theme selector */}
            <Select value={themeId} onValueChange={setThemeId}>
              <SelectTrigger className="h-8 px-2 w-[130px] text-xs text-gray-600 dark:text-gray-300">
                <div className="flex items-center gap-1">
                  <Palette className="w-3 h-3" />
                  <SelectValue placeholder={language === 'ar' ? 'ألوان إيفا' : 'Eva colors'} />
                </div>
              </SelectTrigger>
              <SelectContent>
                {THEME_OPTIONS.map(theme => (
                  <SelectItem key={theme.id} value={theme.id}>
                    <div className="flex items-center gap-2">
                      <span
                        className="inline-block w-3 h-3 rounded-full"
                        style={{ backgroundColor: theme.previewColor }}
                      />
                      <span className="text-xs">{theme.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLanguage(language === 'ar' ? 'en' : 'ar')}
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 h-8 px-2"
            >
              <Globe className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Header with User Info and Logout */}
      {currentUser && (
        <div className="sticky top-0 z-10 bg-white dark:bg-[#343541] border-b border-gray-200 dark:border-gray-700 px-4 py-2">
          <div className="max-w-3xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {currentUser.full_name || currentUser.username}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400"
            >
              <LogOut className="w-4 h-4 mr-1" />
              {language === 'ar' ? 'تسجيل الخروج' : 'Logout'}
            </Button>
          </div>
        </div>
      )}

      {/* Chat Messages - ChatGPT Style */}
      <div className="flex-1 overflow-y-auto bg-[#f7f7f8] dark:bg-[#343541]">
        <div className="max-w-3xl mx-auto">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`group w-full border-b border-gray-200 dark:border-gray-700 ${
                message.isUser 
                  ? 'bg-white dark:bg-[#343541]' 
                  : 'bg-[#f7f7f8] dark:bg-[#444654]'
              }`}
            >
              <div className="flex gap-4 p-4 text-base md:gap-6 md:max-w-2xl md:py-6 lg:max-w-2xl xl:max-w-3xl mx-auto">
                {/* Avatar */}
                <div className="flex-shrink-0 flex flex-col items-end">
                  {message.isUser ? (
                    <div className="w-8 h-8 rounded-full bg-[#19c37d] flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-[#ab68ff] flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
                
                {/* Message Content */}
                <div className="flex-1 min-w-0">
                    {/* Display image if present */}
                    {message.imageBase64 && (
                      <div className="mb-3 rounded-lg overflow-hidden">
                        <img 
                          src={message.imageBase64} 
                          alt="Uploaded" 
                          className="max-w-full h-auto max-h-64 object-contain rounded-lg"
                        />
                      </div>
                    )}
                    
                    {/* ChatGPT-style Markdown rendering */}
                    {!message.isUser ? (
                      <div
                        className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-gray-900 dark:prose-headings:text-gray-100 prose-p:text-gray-800 dark:prose-p:text-gray-200 prose-p:leading-7 prose-p:my-3 prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline prose-strong:text-gray-900 dark:prose-strong:text-gray-100 prose-strong:font-semibold prose-code:text-pink-600 dark:prose-code:text-pink-400 prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono prose-pre:bg-[#282c34] prose-pre:border-0 prose-pre:rounded-lg prose-pre:p-4 prose-pre:overflow-x-auto prose-ul:list-disc prose-ul:pl-6 prose-ul:my-3 prose-ol:list-decimal prose-ol:pl-6 prose-ol:my-3 prose-li:text-gray-800 dark:prose-li:text-gray-200 prose-li:my-1.5 prose-blockquote:border-l-4 prose-blockquote:border-gray-300 dark:prose-blockquote:border-gray-600 prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:my-3 prose-hr:border-gray-200 dark:prose-hr:border-gray-700 prose-hr:my-4 prose-table:text-sm prose-table:w-full prose-table:my-4 prose-th:border prose-th:border-gray-300 dark:prose-th:border-gray-600 prose-th:px-4 prose-th:py-2 prose-th:bg-gray-100 dark:prose-th:bg-gray-800 prose-td:border prose-td:border-gray-300 dark:prose-td:border-gray-600 prose-td:px-4 prose-td:py-2 [&_code]:before:content-none [&_code]:after:content-none [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:text-gray-100"
                      >
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeHighlight, rehypeRaw]}
                          components={{
                            a: ({node, ...props}) => (
                              <a {...props} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                                {props.children}
                              </a>
                            ),
                            code: ({node, inline, className, children, ...props}: any) => {
                              const classNameStr = className ? String(className) : '';
                              const regexPattern = /language-(\w+)/;
                              const match = regexPattern.exec(classNameStr);
                              const newlineRegex = /\n$/;
                              const codeString = String(children).replace(newlineRegex, '');
                              
                              if (!inline && match) {
                                return (
                                  <div className="relative group-code">
                                    <div className="absolute top-2 right-2 opacity-0 group-code-hover:opacity-100 transition-opacity">
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => {
                                          navigator.clipboard.writeText(codeString);
                                          toast({
                                            title: language === 'ar' ? 'تم النسخ' : 'Copied',
                                            description: language === 'ar' ? 'تم نسخ الكود' : 'Code copied to clipboard'
                                          });
                                        }}
                                        className="h-7 w-7 p-0 bg-gray-700 hover:bg-gray-600 text-gray-200"
                                      >
                                        <Copy className="w-3 h-3" />
                                      </Button>
                                    </div>
                                    <pre className="bg-[#282c34] rounded-lg p-4 overflow-x-auto">
                                      <code className={className} {...props}>
                                        {children}
                                      </code>
                                    </pre>
                                  </div>
                                );
                              }
                              return (
                                <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm text-pink-600 dark:text-pink-400 font-mono" {...props}>
                                  {children}
                                </code>
                              );
                            },
                            ul: ({node, ...props}) => (
                              <ul className="list-disc pl-6 space-y-1 my-2" {...props} />
                            ),
                            ol: ({node, ...props}) => (
                              <ol className="list-decimal pl-6 space-y-1 my-2" {...props} />
                            ),
                            li: ({node, ...props}) => (
                              <li className="text-text-primary my-1" {...props} />
                            ),
                            blockquote: ({node, ...props}) => (
                              <blockquote className="border-l-4 border-eva-primary pl-4 italic my-2 text-text-secondary" {...props} />
                            ),
                            hr: ({node, ...props}) => (
                              <hr className="border-chat-border my-4" {...props} />
                            ),
                            p: ({node, ...props}) => (
                              <p className="text-text-primary leading-relaxed my-2" {...props} />
                            ),
                            h1: ({node, ...props}) => (
                              <h1 className="text-2xl font-bold text-text-primary my-3" {...props} />
                            ),
                            h2: ({node, ...props}) => (
                              <h2 className="text-xl font-bold text-text-primary my-2" {...props} />
                            ),
                            h3: ({node, ...props}) => (
                              <h3 className="text-lg font-semibold text-text-primary my-2" {...props} />
                            ),
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">
                        {message.content}
                      </div>
                    )}
                    
                    {/* YouTube video card when available */}
                    {!message.isUser &&
                      message.youtubeVideo &&
                      message.youtubeVideo.video_url &&
                      message.youtubeVideo.thumbnail_url && (
                        <YoutubeCard
                          title={message.youtubeVideo.title}
                          description={message.youtubeVideo.description}
                          thumbnailUrl={message.youtubeVideo.thumbnail_url}
                          videoUrl={message.youtubeVideo.video_url}
                          channelTitle={message.youtubeVideo.channel_title}
                        />
                      )}
                    
                    {/* Action buttons - ChatGPT style */}
                    <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyMessage(message.content)}
                        className="h-7 px-2 text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        title={language === 'ar' ? 'نسخ' : 'Copy'}
                      >
                        <Copy className="w-3 h-3 mr-1" />
                        {language === 'ar' ? 'نسخ' : 'Copy'}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="group w-full border-b border-gray-200 dark:border-gray-700 bg-[#f7f7f8] dark:bg-[#444654]">
              <div className="flex gap-4 p-4 text-base md:gap-6 md:max-w-2xl md:py-6 lg:max-w-2xl xl:max-w-3xl mx-auto">
                <div className="flex-shrink-0 flex flex-col items-end">
                  <div className="w-8 h-8 rounded-full bg-[#ab68ff] flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm ml-2">
                      {language === 'ar' ? 'جارٍ الكتابة...' : 'Thinking...'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area - ChatGPT Style */}
      <div className="sticky bottom-0 left-0 right-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-[#343541] pt-2 pb-2">
        <div className="max-w-3xl mx-auto px-4">
          <div className="flex items-end gap-2 p-3 rounded-2xl bg-white dark:bg-[#40414f] border border-gray-200 dark:border-gray-700 shadow-lg">
            {/* Image Upload Button */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              className="text-text-secondary hover:text-eva-accent transition-colors"
              title={language === 'ar' ? 'رفع صورة' : 'Upload Image'}
              disabled={isLoading}
            >
              <ImageIcon className="w-4 h-4" />
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSpeechRecognition}
              className={`text-text-secondary hover:text-eva-accent transition-colors ${isListening ? 'text-eva-accent animate-pulse' : ''}`}
              title={language === 'ar' ? 'التعرف على الصوت' : 'Speech Recognition'}
              disabled={isLoading}
            >
              {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </Button>
            
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder={
                  language === 'ar'
                    ? 'اكتب رسالتك هنا...'
                    : 'Message Eva...'
                }
                rows={1}:
                className="w-full resize-none border-0 bg-transparent py-3 pr-12 pl-2 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:outline-none focus:ring-0 text-base max-h-[200px] overflow-y-auto"
                disabled={isLoading}
                style={{
                  height: 'auto',
                  minHeight: '24px',
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  const minHeight = Math.min(target.scrollHeight, 200);
                  target.style.height = minHeight + 'px';
                }}
              />
              <Button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                size="sm"
                className="absolute right-2 bottom-2 h-8 w-8 rounded-lg bg-[#19c37d] hover:bg-[#16a269] text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTextToSpeech}
              className={`text-text-secondary hover:text-eva-accent transition-colors ${isSpeaking ? 'text-eva-accent animate-pulse' : ''}`}
              title={language === 'ar' ? 'التحويل إلى صوت' : 'Text to Speech'}
            >
              {isSpeaking ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </Button>
          </div>
          
          </div>
          <div className="text-center mt-2 pb-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {language === 'ar'
                ? 'Eva قد يخطئ. تحقق من المعلومات المهمة.'
                : 'Eva can make mistakes. Check important info.'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvaChatbot;
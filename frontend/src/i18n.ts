import { ref, computed } from "vue";

export type Lang = "en" | "ar";

export const lang = ref<Lang>("en");

const dictionary = {
  en: {
    title: "SmallBiz Guardian AI",
    disclaimer:
      "SmallBiz Guardian AI is an educational planning tool. It is not financial, legal, or tax advice.",
    upload: "1. Upload your sales and expenses",
    checking: "Checking your file...",
    dataCheck: "Data check",
    ready: "Your file is ready.",
    needsFixes: "Your file needs fixes before we can forecast.",
    pleaseFix: "Please fix",
    worthLook: "Worth a look",
    session: "Session started.",
    weeksLoaded: "weeks of data loaded.",
    forecastTitle: "2. Your next 13 weeks",
    forecastNote:
      "The shaded area is a range of likely outcomes. It is an estimate, not a promise.",
    flagsTitle: "3. Things to watch",
    scenariosTitle: "4. Test a decision",
    askTitle: "5. Ask the Guardian",
    askPlaceholder: "Ask about your cash...",
    ask: "Ask",
    choosefile: "Choose file",
    language: "العربية",

    missing_opening_cash:
      "The opening cash balance is missing from the settings.",
    missing_columns: "Missing columns: {columns}",
    invalid_date_format:
      "{count} rows have a date that is not in YYYY-MM-DD format (rows: {rows}).",
    invalid_amount:
      "{count} rows have an amount that is not a number (rows: {rows}).",
    negative_amount: "{count} rows have a negative amount (rows: {rows}).",
    invalid_transaction_type:
      "{count} rows have a type that is not sale or expense (rows: {rows}).",
    unknown_category:
      "{count} rows have an unknown category (rows: {rows}); they will be counted as 'other'.",
    duplicate_rows:
      "{count} rows are exact duplicates of another row (rows: {rows}).",
    dates_far_from_median:
      "{count} rows have dates more than 3 years from the rest of the data, which may indicate a typo (rows: {rows}).",
    data_coverage: "The data covers {first} to {last} ({weeks} weeks).",
    insufficient_history:
      "There are fewer than {minimum} weeks of data, which is not enough to forecast.",
    short_history:
      "There are fewer than {recommended} weeks of data. A forecast is possible, but {recommended} or more is recommended.",
    weeks_without_transactions:
      "{count} weeks have no transactions at all (the first is the week of {first_week}).",
    unknown: "Unknown",
    not_enough_history: "Not enough history (minimum {minimum} weeks).",
    forecast_recommended:
      "Enough to forecast, but {recommended} or more weeks are recommended.",
    fix_errors_first: "Not ready: fix the errors first.",
    enough_history: "Enough history to forecast.",

    cushion_safe:
      "Projected cash stays above your cushion for the next 13 weeks.",
    cushion_breach:
      "Cash is projected to fall below your cushion of {cushion} in week {week}, to {amount}.",

    runway_safe:
      "On the pessimistic forecast, your cash lasts the full 13 weeks.",
    runway_breach:
      "On the pessimistic forecast, your cash runs out in week {weeks}.",

    expense_concentration:
      "{category} is {share} of your spending over the last {weeks} weeks.",
    expense_concentration_safe:
      "No single category is more than 40% of your spending.",

    cost_creep:
      "{category} spending is up {change} compared with 12 weeks ago.",
    cost_creep_safe:
      "No category has risen by more than 15% in the last 12 weeks.",

    revenue_insufficient:
      "There is not enough income in the last 12 weeks to measure.",

    revenue_volatile:
      "Your weekly income has swung by about {cv} of its average over the last {weeks} weeks.",
    revenue_stable:
      "Your weekly income has been fairly steady over the last 12 weeks.",

    fixed_cost_low:
      "Your income covered rent and payroll in only {covered} of the last {weeks} weeks.",
    fixed_cost_good:
      "Your income covered rent and payroll in {covered} of the last {weeks} weeks.",

    cashCushion: "Cash cushion",
    cashCushionWorstCase: "Cash cushion, worst case",
    cashRunway: "How long your cash lasts",
    expenseConcentration: "One cost dominates",
    risingCosts: "Rising costs",
    incomeSwings: "Income swings",
    fixedCostCoverage: "Rent and payroll covered",

    slowSeasonTitle: "Slow season",
    slowSeasonHelp: "What if sales drop for a few weeks?",
    salesDrop: "Sales drop",
    startsInWeek: "Starts in week",
    lastsWeeks: "Lasts (weeks)",

    costShockTitle: "Cost shock",
    costShockHelp: "What if a one-time expense hits?",
    costAmount: "Cost ($)",
    inWeek: "In week",

    priceChangeTitle: "Price change",
    priceChangeHelp: "What if you change your prices?",
    priceChange: "Price change",
    customerReaction: "Customer reaction (0 to 1)",
    addedWeeklyCost: "Added weekly cost ($)",

    lowestCash: "Lowest cash",
    thirteenWeekNet: "13-week net",
    cashCompared: "Your cash compared",
    needTemplate: "Need a template? Download it here:",
    guardlang: "The guardian chat only English currently",
  },
  ar: {
    title: "حارس الأعمال الصغيرة",
    disclaimer:
      "حارس الأعمال الصغيرة أداة تخطيط تعليمية. وليس نصيحة مالية أو قانونية أو ضريبية.",
    upload: "١. ارفع ملف المبيعات والمصروفات",
    checking: "جارٍ فحص الملف...",
    dataCheck: "فحص البيانات",
    ready: "ملفك جاهز.",
    needsFixes: "يحتاج ملفك إلى تعديلات قبل أن نتمكن من التوقع.",
    pleaseFix: "يرجى التصحيح",
    worthLook: "يستحق النظر",
    session: "بدأت الجلسة.",
    weeksLoaded: "أسبوعًا من البيانات تم تحميلها.",
    forecastTitle: "٢. أسابيعك الثلاثة عشر القادمة",
    forecastNote:
      "المنطقة المظللة هي نطاق من النتائج المحتملة. إنها تقدير وليست وعدًا.",
    flagsTitle: "٣. أمور تستحق المراقبة",
    scenariosTitle: "٤. اختبر قرارًا",
    askTitle: "٥. اسأل الحارس",
    askPlaceholder: "اسأل عن نقدك...",
    ask: "اسأل",
    choosefile: "اختر ملفا",
    language: "English",
    missing_opening_cash: "رصيد النقد الافتتاحي غير موجود في الإعدادات.",
    missing_columns: "الأعمدة المفقودة: {columns}",
    invalid_date_format:
      "{count} صفوف تحتوي على تاريخ بتنسيق غير صحيح. يجب استخدام YYYY-MM-DD (الصفوف: {rows}).",
    invalid_amount:
      "{count} صفوف تحتوي على مبلغ ليس رقمًا صحيحًا (الصفوف: {rows}).",
    negative_amount: "{count} صفوف تحتوي على مبالغ سالبة (الصفوف: {rows}).",
    invalid_transaction_type:
      "{count} صفوف تحتوي على نوع معاملة غير صالح. يجب أن يكون sale أو expense (الصفوف: {rows}).",
    unknown_category:
      "{count} صفوف تحتوي على فئة غير معروفة (الصفوف: {rows})، وسيتم احتسابها ضمن فئة أخرى.",
    duplicate_rows: "{count} صفوف مكررة تمامًا (الصفوف: {rows}).",
    dates_far_from_median:
      "{count} صفوف تحتوي على تواريخ تبعد أكثر من 3 سنوات عن بقية البيانات، وقد يشير ذلك إلى خطأ في التاريخ (الصفوف: {rows}).",
    data_coverage:
      "تغطي البيانات الفترة من {first} إلى {last} ({weeks} أسبوعًا).",
    insufficient_history:
      "توجد بيانات لأقل من {minimum} أسبوعًا، وهذا لا يكفي للتنبؤ.",
    short_history:
      "توجد بيانات لأقل من {recommended} أسبوعًا. يمكن إجراء التنبؤ، لكن يُوصى بتوفير {recommended} أسبوعًا أو أكثر.",
    weeks_without_transactions:
      "{count} أسابيع لا تحتوي على أي معاملات (أول أسبوع هو {first_week}).",
    unknown: "غير معروف",
    not_enough_history: "السجل غير كافٍ (الحد الأدنى {minimum} أسبوعًا).",
    forecast_recommended:
      "البيانات كافية للتنبؤ، لكن يُوصى بتوفير {recommended} أسبوعًا أو أكثر.",
    fix_errors_first: "غير جاهز: يرجى إصلاح الأخطاء أولًا.",
    enough_history: "البيانات التاريخية كافية للتنبؤ.",

    cushion_safe:
      "من المتوقع أن يبقى النقد أعلى من الحد الاحتياطي خلال الأسابيع الثلاثة عشر القادمة.",
    cushion_breach:
      "من المتوقع أن ينخفض النقد عن الحد الاحتياطي البالغ {cushion} في الأسبوع {week}، ليصل إلى {amount}.",

    runway_safe:
      "وفقًا للتوقعات المتشائمة، سيكفيك النقد طوال الأسابيع الثلاثة عشر.",
    runway_breach: "وفقًا للتوقعات المتشائمة، سينفد النقد في الأسبوع {weeks}.",

    expense_concentration:
      "تمثل فئة {category} نسبة {share} من مصروفاتك خلال الأسابيع {weeks} الماضية.",
    expense_concentration_safe:
      "لا تمثل أي فئة منفردة أكثر من 40% من مصروفاتك.",

    cost_creep:
      "ارتفعت مصروفات {category} بنسبة {change} مقارنة بما كانت عليه قبل 12 أسبوعًا.",
    cost_creep_safe:
      "لم ترتفع مصروفات أي فئة بأكثر من 15% خلال الأسابيع الاثني عشر الماضية.",

    revenue_insufficient:
      "لا توجد إيرادات كافية خلال الأسابيع الاثني عشر الماضية لقياس التذبذب.",

    revenue_volatile:
      "تذبذب دخلك الأسبوعي بنسبة تقارب {cv} من متوسطه خلال الأسابيع {weeks} الماضية.",
    revenue_stable:
      "كان دخلك الأسبوعي مستقرًا نسبيًا خلال الأسابيع الاثني عشر الماضية.",

    fixed_cost_low:
      "غطى دخلك تكاليف الإيجار والرواتب في {covered} فقط من الأسابيع {weeks} الماضية.",
    fixed_cost_good:
      "غطى دخلك تكاليف الإيجار والرواتب في {covered} من الأسابيع {weeks} الماضية.",

    cashCushion: "الحد الاحتياطي للنقد",
    cashCushionWorstCase: "الحد الاحتياطي للنقد، أسوأ احتمال",
    cashRunway: "المدة التي يكفيك فيها النقد",
    expenseConcentration: "هيمنة فئة واحدة على المصروفات",
    risingCosts: "ارتفاع التكاليف",
    incomeSwings: "تقلبات الدخل",
    fixedCostCoverage: "تغطية الإيجار والرواتب",

    slowSeasonTitle: "موسم الركود",
    slowSeasonHelp: "ماذا لو انخفضت المبيعات لبضعة أسابيع؟",
    salesDrop: "انخفاض المبيعات",
    startsInWeek: "يبدأ في الأسبوع",
    lastsWeeks: "المدة (بالأسابيع)",

    costShockTitle: "صدمة التكاليف",
    costShockHelp: "ماذا لو واجهت مصروفًا لمرة واحدة؟",
    costAmount: "التكلفة ($)",
    inWeek: "في الأسبوع",

    priceChangeTitle: "تغيير الأسعار",
    priceChangeHelp: "ماذا لو قمت بتغيير أسعارك؟",
    priceChange: "تغيير السعر",
    customerReaction: "استجابة العملاء (من 0 إلى 1)",
    addedWeeklyCost: "التكلفة الأسبوعية الإضافية ($)",

    lowestCash: "أقل رصيد نقدي",
    thirteenWeekNet: "صافي التدفق خلال 13 أسبوعًا",
    cashCompared: "مقارنة رصيدك النقدي",
    needTemplate: "تحتاج إلى قالب؟ حمّله من هنا:",
    guardlang: "الحارس يتكلم فقط الانجليزية في الوقت الحالي ",
  },
};

export type Key = keyof typeof dictionary.en;

export function t(key: Key): string {
  return dictionary[lang.value][key];
}

export function translateMessage(
  code: string,
  params: Record<string, string | number> = {},
): string {
  const messages = dictionary[lang.value] as Record<string, string>;

  let result = messages[code] ?? code;

  for (const [key, value] of Object.entries(params)) {
    result = result.replaceAll(`{${key}}`, String(value));
  }

  return result;
}

export const dir = computed(() => (lang.value === "ar" ? "rtl" : "ltr"));

export function toggleLanguage() {
  lang.value = lang.value === "en" ? "ar" : "en";
  document.documentElement.dir = dir.value;
  document.documentElement.lang = lang.value;
}

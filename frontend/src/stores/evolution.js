import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import { soundManager } from '@/utils/sound'

// ========================================
// 施設マスターデータ（60個の施設）
// ========================================
const FACILITIES_MASTER = [
  // ═══════════════════════════════════════════════
  // Era 1: 黎明期 [Solitary Dawn] - 孤独な自習室
  // 累計KP: 0 → 10,000
  // ═══════════════════════════════════════════════
  {
    id: 'notebook',
    name: '学習ノート',
    description: '全ての始まり。一冊のノートから知識が広がる。',
    baseCost: 10,
    baseProduction: 0.1,
    unlockCondition: 0,
    tier: 1,
    icon: '📓',
    flavorText: '「千里の道も一歩から」'
  },
  {
    id: 'pencil_set',
    name: '高級筆記具セット',
    description: '書く喜びが学習効率を高める。',
    baseCost: 25,
    baseProduction: 0.3,
    unlockCondition: 15,
    tier: 1,
    icon: '✏️',
    flavorText: 'ペンは剣より強し'
  },
  {
    id: 'desk_lamp',
    name: 'デスクライト',
    description: '集中力を照らす光。夜間学習の必需品。',
    baseCost: 50,
    baseProduction: 0.5,
    unlockCondition: 40,
    tier: 1,
    icon: '💡',
    flavorText: '暗闇の中でも学びは続く'
  },
  {
    id: 'bookshelf',
    name: '本棚',
    description: '知識のストック。参考書を整理して効率アップ。',
    baseCost: 100,
    baseProduction: 1,
    unlockCondition: 80,
    tier: 1,
    icon: '📚',
    flavorText: '本棚は知識の城'
  },
  {
    id: 'study_desk',
    name: '学習デスク',
    description: '専用の学習空間。姿勢が良くなり集中力向上。',
    baseCost: 200,
    baseProduction: 2,
    unlockCondition: 150,
    tier: 1,
    icon: '🪑',
    flavorText: '机に向かうことが習慣に'
  },
  {
    id: 'pc_setup',
    name: 'PCセットアップ',
    description: 'デジタル時代の学習環境。無限の情報にアクセス。',
    baseCost: 400,
    baseProduction: 4,
    unlockCondition: 300,
    tier: 1,
    icon: '💻',
    flavorText: 'インターネットは知識の海'
  },
  {
    id: 'coffee_maker',
    name: 'コーヒーメーカー',
    description: 'カフェインで集中力を持続。長時間学習のお供。',
    baseCost: 800,
    baseProduction: 8,
    unlockCondition: 600,
    tier: 1,
    icon: '☕',
    flavorText: '一杯のコーヒーが脳を目覚めさせる'
  },
  {
    id: 'noise_canceling',
    name: 'ノイキャンヘッドホン',
    description: '雑音を遮断。完璧な集中環境を構築。',
    baseCost: 1500,
    baseProduction: 15,
    unlockCondition: 1000,
    tier: 1,
    icon: '🎧',
    flavorText: '沈黙こそ最高のBGM'
  },
  {
    id: 'einstein_poster',
    name: 'アインシュタインのポスター',
    description: '偉人の眼差しが学習を見守る。',
    baseCost: 3000,
    baseProduction: 30,
    unlockCondition: 2000,
    tier: 1,
    icon: '🖼️',
    flavorText: '「想像力は知識より重要だ」'
  },
  {
    id: 'study_room',
    name: '専用自習室',
    description: '完璧に設計された個人学習空間の完成。',
    baseCost: 6000,
    baseProduction: 60,
    unlockCondition: 4000,
    tier: 1,
    icon: '🏠',
    flavorText: 'ここから全てが始まった'
  },

  // ═══════════════════════════════════════════════
  // Era 2: 躍進期 [Rising Foundation] - 地上研究拠点
  // 累計KP: 10,000 → 500,000
  // ═══════════════════════════════════════════════
  {
    id: 'lab_bench',
    name: '実験台',
    description: '本格的な実験が可能に。理論を実践で検証。',
    baseCost: 12000,
    baseProduction: 100,
    unlockCondition: 8000,
    tier: 2,
    icon: '🔬',
    flavorText: '実験は真実への扉'
  },
  {
    id: 'microscope',
    name: '電子顕微鏡',
    description: 'ミクロの世界を覗く。原子レベルの観察が可能。',
    baseCost: 25000,
    baseProduction: 200,
    unlockCondition: 15000,
    tier: 2,
    icon: '🔭',
    flavorText: '見えない世界が見えてくる'
  },
  {
    id: 'server_rack',
    name: 'サーバーラック',
    description: '膨大なデータを処理。計算能力が飛躍的に向上。',
    baseCost: 50000,
    baseProduction: 400,
    unlockCondition: 30000,
    tier: 2,
    icon: '🖥️',
    flavorText: 'データは新しい石油'
  },
  {
    id: 'research_team',
    name: '研究チーム',
    description: '優秀な研究員を雇用。集合知の力を解放。',
    baseCost: 100000,
    baseProduction: 800,
    unlockCondition: 60000,
    tier: 2,
    icon: '👨‍🔬',
    flavorText: '三人寄れば文殊の知恵'
  },
  {
    id: 'quantum_computer',
    name: '量子コンピュータ',
    description: '量子力学の原理で計算。従来の限界を突破。',
    baseCost: 200000,
    baseProduction: 1500,
    unlockCondition: 120000,
    tier: 2,
    icon: '🧮',
    flavorText: '0と1が同時に存在する世界'
  },
  {
    id: 'ai_assistant',
    name: 'AI学習アシスタント',
    description: '人工知能が学習を最適化。24時間のサポート。',
    baseCost: 400000,
    baseProduction: 3000,
    unlockCondition: 200000,
    tier: 2,
    icon: '🤖',
    flavorText: 'AIは最高の家庭教師'
  },
  {
    id: 'library',
    name: '私設図書館',
    description: '膨大な蔵書を所有。あらゆる知識にアクセス可能。',
    baseCost: 800000,
    baseProduction: 6000,
    unlockCondition: 350000,
    tier: 2,
    icon: '🏛️',
    flavorText: '本は人類の記憶'
  },
  {
    id: 'super_computer',
    name: 'スパコン「富岳」',
    description: '世界最高峰の計算能力。',
    baseCost: 1500000,
    baseProduction: 12000,
    unlockCondition: 500000,
    tier: 2,
    icon: '🖲️',
    flavorText: '1秒で4京回の計算'
  },
  {
    id: 'research_center',
    name: 'JAXA研究棟',
    description: '国立研究機関との共同研究。宇宙開発の第一歩。',
    baseCost: 3000000,
    baseProduction: 25000,
    unlockCondition: 800000,
    tier: 2,
    icon: '🏢',
    flavorText: '宇宙への扉が開く'
  },
  {
    id: 'phd',
    name: '博士号取得',
    description: '学術界の頂点に到達。研究者としての地位を確立。',
    baseCost: 6000000,
    baseProduction: 50000,
    unlockCondition: 1200000,
    tier: 2,
    icon: '🎓',
    flavorText: 'Dr.の称号を手に入れた'
  },

  // ═══════════════════════════════════════════════
  // Era 3: 超越期 [Orbital Transcendence] - 軌道上への進出
  // 累計KP: 500,000 → 50,000,000
  // ═══════════════════════════════════════════════
  {
    id: 'satellite',
    name: '観測衛星',
    description: '地球軌道に衛星を配置。宇宙からの視点を獲得。',
    baseCost: 12000000,
    baseProduction: 100000,
    unlockCondition: 2000000,
    tier: 3,
    icon: '🛰️',
    flavorText: '地球は青かった'
  },
  {
    id: 'space_center',
    name: '種子島宇宙センター',
    description: '九州から宇宙へ。ロケット打ち上げ施設を運営。',
    baseCost: 25000000,
    baseProduction: 200000,
    unlockCondition: 5000000,
    tier: 3,
    icon: '🚀',
    flavorText: '3, 2, 1... リフトオフ！'
  },
  {
    id: 'orbital_elevator_base',
    name: '軌道エレベータ基部',
    description: '宇宙への高速道路。建設が始まる。',
    baseCost: 50000000,
    baseProduction: 400000,
    unlockCondition: 10000000,
    tier: 3,
    icon: '🏗️',
    flavorText: '天まで届く塔を建てよう'
  },
  {
    id: 'iss',
    name: '国際宇宙ステーション',
    description: '無重力環境での研究。国際協力の象徴。',
    baseCost: 100000000,
    baseProduction: 800000,
    unlockCondition: 20000000,
    tier: 3,
    icon: '🌐',
    flavorText: '宇宙は国境を超える'
  },
  {
    id: 'space_solar',
    name: '宇宙太陽光発電',
    description: '無限のクリーンエネルギー。24時間発電可能。',
    baseCost: 200000000,
    baseProduction: 1500000,
    unlockCondition: 40000000,
    tier: 3,
    icon: '☀️',
    flavorText: '太陽の恵みを直接受ける'
  },
  {
    id: 'space_factory',
    name: '宇宙工場',
    description: '無重力製造。地上では不可能な精密加工。',
    baseCost: 400000000,
    baseProduction: 3000000,
    unlockCondition: 80000000,
    tier: 3,
    icon: '🏭',
    flavorText: '重力に縛られない製造'
  },
  {
    id: 'orbital_hotel',
    name: '軌道ホテル',
    description: '宇宙観光の拠点。一般人も宇宙を体験。',
    baseCost: 800000000,
    baseProduction: 6000000,
    unlockCondition: 150000000,
    tier: 3,
    icon: '🏨',
    flavorText: '地球を眺めながらの朝食'
  },
  {
    id: 'orbital_elevator',
    name: '軌道エレベータ完成',
    description: '宇宙への大動脈が完成。輸送コストが劇的に低下。',
    baseCost: 1500000000,
    baseProduction: 12000000,
    unlockCondition: 300000000,
    tier: 3,
    icon: '🗼',
    flavorText: 'カーボンナノチューブの奇跡'
  },
  {
    id: 'debris_cleaner',
    name: 'デブリ除去システム',
    description: '宇宙ゴミを一掃。軌道環境を保全。',
    baseCost: 3000000000,
    baseProduction: 25000000,
    unlockCondition: 600000000,
    tier: 3,
    icon: '🧹',
    flavorText: '宇宙も掃除が大切'
  },
  {
    id: 'orbital_city',
    name: '軌道都市「テンカワ」',
    description: '宇宙で暮らす時代の到来。人口1万人の都市。',
    baseCost: 6000000000,
    baseProduction: 50000000,
    unlockCondition: 1000000000,
    tier: 3,
    icon: '🌆',
    flavorText: '宇宙市民第一号になろう'
  },

  // ═══════════════════════════════════════════════
  // Era 4: 開拓期 [Planetary Federation] - 惑星間文明
  // ═══════════════════════════════════════════════
  {
    id: 'lunar_outpost',
    name: '月面前哨基地',
    description: '月に第一歩。恒久的な居住施設を建設。',
    baseCost: 15000000000,
    baseProduction: 100000000,
    unlockCondition: 2000000000,
    tier: 4,
    icon: '🌙',
    flavorText: '月は人類の足がかり'
  },
  {
    id: 'helium3_mining',
    name: 'ヘリウム3採掘',
    description: '月面から核融合燃料を採掘。エネルギー革命。',
    baseCost: 30000000000,
    baseProduction: 200000000,
    unlockCondition: 5000000000,
    tier: 4,
    icon: '⛏️',
    flavorText: '夢のエネルギー源'
  },
  {
    id: 'mars_lander',
    name: '火星着陸船',
    description: '赤い惑星への第一歩。有人火星探査を実現。',
    baseCost: 60000000000,
    baseProduction: 400000000,
    unlockCondition: 10000000000,
    tier: 4,
    icon: '🔴',
    flavorText: '火星に足跡を残す'
  },
  {
    id: 'mars_dome',
    name: '火星ドーム都市',
    description: '火星での居住が可能に。テラフォーミングの拠点。',
    baseCost: 120000000000,
    baseProduction: 800000000,
    unlockCondition: 25000000000,
    tier: 4,
    icon: '🏙️',
    flavorText: '赤い砂漠に緑を'
  },
  {
    id: 'terraforming',
    name: '火星テラフォーミング',
    description: '惑星改造計画。火星を第二の地球に。',
    baseCost: 250000000000,
    baseProduction: 1500000000,
    unlockCondition: 50000000000,
    tier: 4,
    icon: '🌍',
    flavorText: '100年計画の始まり'
  },
  {
    id: 'asteroid_mining',
    name: '小惑星採掘船団',
    description: '宇宙資源を獲得。レアメタルの宝庫。',
    baseCost: 500000000000,
    baseProduction: 3000000000,
    unlockCondition: 100000000000,
    tier: 4,
    icon: '☄️',
    flavorText: '一つの小惑星で地球のGDPを超える'
  },
  {
    id: 'jupiter_station',
    name: '木星軌道ステーション',
    description: '巨大ガス惑星の衛星を探査。外惑星進出の拠点。',
    baseCost: 1000000000000,
    baseProduction: 6000000000,
    unlockCondition: 200000000000,
    tier: 4,
    icon: '🪐',
    flavorText: '巨人の王国へ'
  },
  {
    id: 'titan_base',
    name: 'タイタン資源基地',
    description: '土星の月タイタンで液体メタンを採取。',
    baseCost: 2000000000000,
    baseProduction: 12000000000,
    unlockCondition: 400000000000,
    tier: 4,
    icon: '🌕',
    flavorText: 'メタンの海を航行する'
  },
  {
    id: 'europa_submarine',
    name: 'エウロパ海底探査',
    description: '氷の下の海を探る。地球外生命の可能性。',
    baseCost: 4000000000000,
    baseProduction: 25000000000,
    unlockCondition: 800000000000,
    tier: 4,
    icon: '🌊',
    flavorText: '私たちは孤独ではない…かもしれない'
  },
  {
    id: 'federation',
    name: '惑星間連邦議会',
    description: '太陽系全域を統治する政府。新時代の幕開け。',
    baseCost: 8000000000000,
    baseProduction: 50000000000,
    unlockCondition: 1500000000000,
    tier: 4,
    icon: '⚖️',
    flavorText: '太陽系は一つになった'
  },

  // ═══════════════════════════════════════════════
  // Era 5: 銀河期 [Stellar Ascension] - 恒星間航行
  // ═══════════════════════════════════════════════
  {
    id: 'alpha_probe',
    name: 'αケンタウリ探査機',
    description: '最も近い恒星系へ。光速の10%で航行。',
    baseCost: 20000000000000,
    baseProduction: 100000000000,
    unlockCondition: 3000000000000,
    tier: 5,
    icon: '⭐',
    flavorText: '最も近い隣人へ'
  },
  {
    id: 'dyson_swarm',
    name: 'ダイソンスウォーム',
    description: '太陽を取り囲む衛星群。恒星エネルギーの一部を回収。',
    baseCost: 50000000000000,
    baseProduction: 200000000000,
    unlockCondition: 8000000000000,
    tier: 5,
    icon: '🌞',
    flavorText: '太陽の力を手中に'
  },
  {
    id: 'antimatter_engine',
    name: '反物質エンジン',
    description: 'E=mc²の力を推進に。光速の50%を実現。',
    baseCost: 100000000000000,
    baseProduction: 400000000000,
    unlockCondition: 20000000000000,
    tier: 5,
    icon: '⚛️',
    flavorText: '物質と反物質の出会い'
  },
  {
    id: 'warp_prototype',
    name: 'ワープドライブ試作機',
    description: '時空を歪める。アルクビエレ・ドライブの実験。',
    baseCost: 250000000000000,
    baseProduction: 800000000000,
    unlockCondition: 50000000000000,
    tier: 5,
    icon: '🌀',
    flavorText: '空間そのものを動かす'
  },
  {
    id: 'dyson_sphere',
    name: 'ダイソン球殻完成',
    description: '太陽を完全に包む。恒星エネルギーの100%を利用。',
    baseCost: 500000000000000,
    baseProduction: 1500000000000,
    unlockCondition: 100000000000000,
    tier: 5,
    icon: '🔆',
    flavorText: 'タイプII文明への到達'
  },
  {
    id: 'warp_gate',
    name: 'ワープゲート',
    description: '恒星間を瞬時に移動。銀河ハイウェイの建設。',
    baseCost: 1000000000000000,
    baseProduction: 3000000000000,
    unlockCondition: 200000000000000,
    tier: 5,
    icon: '🚪',
    flavorText: '一歩で100光年'
  },
  {
    id: 'first_contact',
    name: 'ファーストコンタクト',
    description: '私たちは孤独ではなかった。銀河の仲間入り。',
    baseCost: 2500000000000000,
    baseProduction: 6000000000000,
    unlockCondition: 400000000000000,
    tier: 5,
    icon: '👽',
    flavorText: 'We are not alone'
  },
  {
    id: 'galactic_council',
    name: '銀河評議会加盟',
    description: '銀河文明の一員として認められる。',
    baseCost: 5000000000000000,
    baseProduction: 12000000000000,
    unlockCondition: 800000000000000,
    tier: 5,
    icon: '🏛️',
    flavorText: '銀河市民権を獲得'
  },
  {
    id: 'galactic_network',
    name: '銀河通信ネットワーク',
    description: '銀河全域でリアルタイム通信が可能に。',
    baseCost: 10000000000000000,
    baseProduction: 25000000000000,
    unlockCondition: 1500000000000000,
    tier: 5,
    icon: '📡',
    flavorText: '10万光年を超えて繋がる'
  },
  {
    id: 'galactic_president',
    name: '銀河連邦大統領',
    description: '銀河文明のリーダーに選出。歴史に名を残す。',
    baseCost: 25000000000000000,
    baseProduction: 50000000000000,
    unlockCondition: 3000000000000000,
    tier: 5,
    icon: '👑',
    flavorText: '全宇宙の意思を導く者'
  },

  // ═══════════════════════════════════════════════
  // Era 6: 終焉と新生 [Singularity & Rebirth]
  // ═══════════════════════════════════════════════
  {
    id: 'mind_upload',
    name: '意識のデジタル化',
    description: '肉体の限界を超える。精神をデータ化。',
    baseCost: 50000000000000000,
    baseProduction: 100000000000000,
    unlockCondition: 5000000000000000,
    tier: 6,
    icon: '🧠',
    flavorText: '永遠の命を手に入れる'
  },
  {
    id: 'black_hole_engine',
    name: 'ブラックホールエンジン',
    description: '特異点からエネルギーを抽出。究極の動力源。',
    baseCost: 100000000000000000,
    baseProduction: 200000000000000,
    unlockCondition: 10000000000000000,
    tier: 6,
    icon: '🕳️',
    flavorText: '闇の中に無限の光がある'
  },
  {
    id: 'time_reversal',
    name: '時間逆行装置',
    description: '因果律を操作。過去への干渉が可能に。',
    baseCost: 250000000000000000,
    baseProduction: 400000000000000,
    unlockCondition: 25000000000000000,
    tier: 6,
    icon: '⏰',
    flavorText: '時は流れを変える'
  },
  {
    id: 'parallel_observer',
    name: '並行宇宙観測',
    description: '多世界解釈を実証。無限の可能性を垣間見る。',
    baseCost: 500000000000000000,
    baseProduction: 800000000000000,
    unlockCondition: 50000000000000000,
    tier: 6,
    icon: '🪞',
    flavorText: '全ての選択肢が存在する'
  },
  {
    id: 'dark_matter_control',
    name: 'ダークマター操作',
    description: '宇宙の26%を占める物質を制御。',
    baseCost: 1e18,
    baseProduction: 1500000000000000,
    unlockCondition: 100000000000000000,
    tier: 6,
    icon: '🌑',
    flavorText: '見えない力を支配する'
  },
  {
    id: 'dark_energy_harvest',
    name: 'ダークエネルギー収穫',
    description: '宇宙の68%を占めるエネルギーを利用。',
    baseCost: 2.5e18,
    baseProduction: 3000000000000000,
    unlockCondition: 250000000000000000,
    tier: 6,
    icon: '✴️',
    flavorText: '宇宙そのものがエネルギー'
  },
  {
    id: 'planet_forge',
    name: '惑星創造',
    description: '物質を自在に操り、新しい惑星を生み出す。',
    baseCost: 5e18,
    baseProduction: 6000000000000000,
    unlockCondition: 500000000000000000,
    tier: 6,
    icon: '🌍',
    flavorText: '神の業を手に入れた'
  },
  {
    id: 'star_forge',
    name: '恒星創造',
    description: '核融合を自在に起動。新しい太陽を生み出す。',
    baseCost: 1e19,
    baseProduction: 12000000000000000,
    unlockCondition: 1e18,
    tier: 6,
    icon: '⭐',
    flavorText: '光あれ、と言った'
  },
  {
    id: 'galaxy_forge',
    name: '銀河創造',
    description: '数千億の恒星を含む銀河を設計・創造。',
    baseCost: 2.5e19,
    baseProduction: 25000000000000000,
    unlockCondition: 2.5e18,
    tier: 6,
    icon: '🌌',
    flavorText: '渦巻く星々の母となる'
  },
  {
    id: 'singularity',
    name: '技術的特異点',
    description: '全てを超越。無限の知性が誕生。宇宙を再定義する力。',
    baseCost: 1e20,
    baseProduction: 100000000000000000,
    unlockCondition: 1e19,
    tier: 6,
    icon: '✨',
    flavorText: 'そして、新しい宇宙が始まる...'
  }
]

// ========================================
// アップグレードマスターデータ
// ========================================
const UPGRADES_MASTER = [
  // Era 1 Upgrades
  { id: 'better_pencils', name: '高品質鉛筆', description: 'ノートの効率が2倍', cost: 100, unlockCondition: { facility: 'notebook', level: 10 }, effect: { type: 'multiply', target: 'notebook', value: 2 }, icon: '✏️' },
  { id: 'ergonomic_chair', name: 'エルゴノミクスチェア', description: '学習デスクの効率が2倍', cost: 1000, unlockCondition: { facility: 'study_desk', level: 10 }, effect: { type: 'multiply', target: 'study_desk', value: 2 }, icon: '🪑' },
  { id: 'dual_monitors', name: 'デュアルモニター', description: 'PCの効率が2倍', cost: 2000, unlockCondition: { facility: 'pc_setup', level: 10 }, effect: { type: 'multiply', target: 'pc_setup', value: 2 }, icon: '🖥️' },
  { id: 'global_1', name: '集中力トレーニング', description: '全施設+10%', cost: 5000, unlockCondition: { totalKP: 3000 }, effect: { type: 'global_multiply', value: 1.1 }, icon: '🧘' },

  // Era 2 Upgrades
  { id: 'ai_optimization', name: 'AI最適化', description: 'AIアシスタントの効率が3倍', cost: 500000, unlockCondition: { facility: 'ai_assistant', level: 10 }, effect: { type: 'multiply', target: 'ai_assistant', value: 3 }, icon: '🤖' },
  { id: 'quantum_upgrade', name: '量子ビット増強', description: '量子コンピュータの効率が3倍', cost: 300000, unlockCondition: { facility: 'quantum_computer', level: 10 }, effect: { type: 'multiply', target: 'quantum_computer', value: 3 }, icon: '⚛️' },
  { id: 'global_2', name: '研究方法論の革新', description: '全施設+25%', cost: 1000000, unlockCondition: { totalKP: 500000 }, effect: { type: 'global_multiply', value: 1.25 }, icon: '📈' },

  // Era 3+ Upgrades
  { id: 'space_efficiency', name: '宇宙開発効率化', description: 'Era3施設の効率が2倍', cost: 50000000, unlockCondition: { totalKP: 10000000 }, effect: { type: 'tier_multiply', target: 3, value: 2 }, icon: '🚀' },
  { id: 'planetary_synergy', name: '惑星間シナジー', description: 'Era4施設の効率が2倍', cost: 5e12, unlockCondition: { totalKP: 1e12 }, effect: { type: 'tier_multiply', target: 4, value: 2 }, icon: '🪐' },
  { id: 'galactic_wisdom', name: '銀河の叡智', description: 'Era5施設の効率が3倍', cost: 1e15, unlockCondition: { totalKP: 1e14 }, effect: { type: 'tier_multiply', target: 5, value: 3 }, icon: '🌌' },
  { id: 'cosmic_transcendence', name: '宇宙的超越', description: '全施設の効率が2倍', cost: 1e20, unlockCondition: { totalKP: 1e19 }, effect: { type: 'global_multiply', value: 2 }, icon: '✨' }
]

// ========================================
// 実績マスターデータ
// ========================================
const ACHIEVEMENTS_MASTER = [
  { id: 'kp_100', name: '初めの一歩', description: '100 KPを獲得', condition: { type: 'totalKP', value: 100 }, icon: '🌱' },
  { id: 'kp_1000', name: '知識の芽生え', description: '1,000 KPを獲得', condition: { type: 'totalKP', value: 1000 }, icon: '🌿' },
  { id: 'kp_10000', name: '研究者への道', description: '10,000 KPを獲得', condition: { type: 'totalKP', value: 10000 }, icon: '🌳' },
  { id: 'kp_1m', name: '学者の領域', description: '100万KPを獲得', condition: { type: 'totalKP', value: 1e6 }, icon: '🏛️' },
  { id: 'kp_1b', name: '宇宙への扉', description: '10億KPを獲得', condition: { type: 'totalKP', value: 1e9 }, icon: '🚀' },
  { id: 'kp_1t', name: '惑星の支配者', description: '1兆KPを獲得', condition: { type: 'totalKP', value: 1e12 }, icon: '🪐' },
  { id: 'kp_1qa', name: '銀河の覇者', description: '1京KPを獲得', condition: { type: 'totalKP', value: 1e16 }, icon: '🌌' },
  { id: 'facility_10', name: '施設マニア', description: '施設レベル合計10', condition: { type: 'totalLevel', value: 10 }, icon: '🏗️' },
  { id: 'facility_100', name: '建設王', description: '施設レベル合計100', condition: { type: 'totalLevel', value: 100 }, icon: '🏰' },
  { id: 'facility_1000', name: '帝国の建築家', description: '施設レベル合計1000', condition: { type: 'totalLevel', value: 1000 }, icon: '🌆' },
  { id: 'prestige_1', name: '学年進級', description: '初めての転生', condition: { type: 'prestigeCount', value: 1 }, icon: '🔄' },
  { id: 'prestige_5', name: '学習の輪廻', description: '5回転生', condition: { type: 'prestigeCount', value: 5 }, icon: '♻️' },
  { id: 'prestige_10', name: '永劫回帰', description: '10回転生', condition: { type: 'prestigeCount', value: 10 }, icon: '🌀' }
]

// Tier情報
const TIER_INFO = {
  1: { name: '黎明期', color: 'from-slate-400 to-slate-600', bgColor: 'bg-slate-100' },
  2: { name: '躍進期', color: 'from-blue-400 to-blue-600', bgColor: 'bg-blue-50' },
  3: { name: '超越期', color: 'from-purple-400 to-purple-600', bgColor: 'bg-purple-50' },
  4: { name: '開拓期', color: 'from-orange-400 to-red-500', bgColor: 'bg-orange-50' },
  5: { name: '銀河期', color: 'from-pink-400 to-purple-600', bgColor: 'bg-pink-50' },
  6: { name: '終焉と新生', color: 'from-yellow-400 to-amber-500', bgColor: 'bg-amber-50' }
}

// 数値フォーマット用接尾辞
const NUMBER_SUFFIXES = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc', 'UDc', 'DDc', 'TDc', 'QaDc', 'QiDc', 'SxDc', 'SpDc', 'OcDc', 'NoDc', 'Vg', 'Ce']

export const useEvolutionStore = defineStore('evolution', () => {
  const userStore = useUserStore()

  // ===== State =====
  const knowledgePoints = ref(0)
  const totalEarnedPoints = ref(0)
  const lifetimeEarnedPoints = ref(0)
  const facilityLevels = ref({})
  const purchasedUpgrades = ref([])
  const unlockedAchievements = ref([])

  // 転生システム
  const prestigeLevel = ref(0)
  const prestigePoints = ref(0)
  const prestigeMultiplier = ref(1)

  // オフライン報酬
  const lastActiveTime = ref(Date.now())
  const pendingOfflineReward = ref(0)

  // UI状態
  const lastSyncTime = ref(null)
  const isDirty = ref(false)

  // イベントバス
  const eventBus = ref({})

  // ===== Helper Functions =====
  const getUpgradeMultiplier = (facilityId, tier) => {
    let mult = 1
    for (const upgradeId of purchasedUpgrades.value) {
      const upgrade = UPGRADES_MASTER.find(u => u.id === upgradeId)
      if (!upgrade) continue
      if (upgrade.effect.type === 'multiply' && upgrade.effect.target === facilityId) mult *= upgrade.effect.value
      if (upgrade.effect.type === 'tier_multiply' && upgrade.effect.target === tier) mult *= upgrade.effect.value
      if (upgrade.effect.type === 'global_multiply') mult *= upgrade.effect.value
    }
    return mult
  }

  // マイルストーンボーナス計算
  const getMilestoneBonus = (level) => {
    let bonus = 1
    const milestones = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
    for (const m of milestones) {
      if (level >= m) bonus *= 2
    }
    return bonus
  }

  // ===== Computed =====
  const currentProduction = computed(() => {
    let production = 0
    for (const facility of FACILITIES_MASTER) {
      const level = facilityLevels.value[facility.id] || 0
      if (level > 0) {
        const upgradeMult = getUpgradeMultiplier(facility.id, facility.tier)
        const milestoneBonus = getMilestoneBonus(level)
        production += facility.baseProduction * level * upgradeMult * prestigeMultiplier.value * milestoneBonus
      }
    }
    return production
  })

  const totalMultiplier = computed(() => {
    let mult = 1.0
    for (const facility of FACILITIES_MASTER) {
      const level = facilityLevels.value[facility.id] || 0
      if (level > 0) mult += facility.baseProduction * level * 0.01
    }
    for (const upgradeId of purchasedUpgrades.value) {
      const upgrade = UPGRADES_MASTER.find(u => u.id === upgradeId)
      if (upgrade?.effect.type === 'global_multiply') mult *= upgrade.effect.value
    }
    return mult * prestigeMultiplier.value
  })

  const facilitiesWithState = computed(() => {
    return FACILITIES_MASTER.map(facility => {
      const level = facilityLevels.value[facility.id] || 0
      const currentCost = calculateCost(facility.baseCost, level)

      // マイルストーンボーナス計算
      let milestoneBonus = 1
      const milestones = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
      for (const m of milestones) {
        if (level >= m) milestoneBonus *= 2
      }

      const upgradeMult = getUpgradeMultiplier(facility.id, facility.tier)
      const baseProduction = facility.baseProduction * Math.max(1, level) * upgradeMult * prestigeMultiplier.value
      const production = baseProduction * milestoneBonus

      let state = 'locked'
      if (totalEarnedPoints.value >= facility.unlockCondition) state = 'unlocked'
      else if (totalEarnedPoints.value >= facility.unlockCondition * 0.7) state = 'revealed'
      else if (totalEarnedPoints.value >= facility.unlockCondition * 0.3) state = 'hint'

      // 次のマイルストーン情報
      let nextMilestone = null
      for (const m of milestones) {
        if (level < m) {
          nextMilestone = { target: m, progress: (level / m) * 100, bonus: milestoneBonus * 2 }
          break
        }
      }

      return {
        ...facility,
        level,
        currentCost,
        production,
        milestoneBonus,
        nextMilestone,
        state,
        canAfford: knowledgePoints.value >= currentCost && state === 'unlocked',
        progressToUnlock: Math.min(100, (totalEarnedPoints.value / facility.unlockCondition) * 100),
        upgradeMultiplier: upgradeMult
      }
    })
  })

  const facilitiesByTier = computed(() => {
    const grouped = {}
    for (const facility of facilitiesWithState.value) {
      if (!grouped[facility.tier]) {
        grouped[facility.tier] = { ...TIER_INFO[facility.tier], tier: facility.tier, facilities: [] }
      }
      grouped[facility.tier].facilities.push(facility)
    }
    return Object.values(grouped).sort((a, b) => a.tier - b.tier)
  })

  const upgradesWithState = computed(() => {
    return UPGRADES_MASTER.map(upgrade => {
      const purchased = purchasedUpgrades.value.includes(upgrade.id)
      let unlocked = false
      if (upgrade.unlockCondition.facility) {
        const level = facilityLevels.value[upgrade.unlockCondition.facility] || 0
        unlocked = level >= upgrade.unlockCondition.level
      } else if (upgrade.unlockCondition.totalKP) {
        unlocked = totalEarnedPoints.value >= upgrade.unlockCondition.totalKP
      }
      return { ...upgrade, purchased, unlocked: unlocked || purchased, canAfford: knowledgePoints.value >= upgrade.cost && !purchased && unlocked }
    })
  })

  const availableUpgrades = computed(() => upgradesWithState.value.filter(u => u.unlocked && !u.purchased))

  const nextUnlock = computed(() => facilitiesWithState.value.find(f => f.state !== 'unlocked'))

  const currentEra = computed(() => {
    let maxTier = 1
    for (const f of facilitiesWithState.value) {
      if (f.state === 'unlocked' && f.tier > maxTier) maxTier = f.tier
    }
    return maxTier
  })

  const potentialPrestigePoints = computed(() => {
    if (totalEarnedPoints.value < 1e9) return 0
    return Math.floor(Math.pow(Math.log10(totalEarnedPoints.value), 1.5))
  })

  const stats = computed(() => {
    const totalOwned = Object.values(facilityLevels.value).reduce((a, b) => a + b, 0)
    const unlockedCount = facilitiesWithState.value.filter(f => f.state === 'unlocked').length
    return {
      totalOwned,
      unlockedCount,
      totalFacilities: FACILITIES_MASTER.length,
      multiplier: totalMultiplier.value,
      production: currentProduction.value,
      prestigeLevel: prestigeLevel.value,
      prestigeMultiplier: prestigeMultiplier.value,
      currentEra: currentEra.value
    }
  })

  // ===== Actions =====
  // コスト計算: baseCost × 1.15^level
  // Cookie Clicker と同じ係数だが、マイルストーンボーナスで緩和
  function calculateCost(baseCost, level) {
    return Math.floor(baseCost * Math.pow(1.15, level))
  }

  // 施設の生産量計算（マイルストーンボーナス込み）
  function getFacilityProduction(facility, level) {
    if (level <= 0) return 0

    let bonus = 1
    // マイルストーンボーナス: 各閾値で +100%（2倍）
    // 10個: 2x, 25個: 4x, 50個: 8x, 100個: 16x, 150個: 32x, 200個: 64x
    const milestones = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
    for (const m of milestones) {
      if (level >= m) bonus *= 2
    }

    const upgradeMult = getUpgradeMultiplier(facility.id, facility.tier)
    return facility.baseProduction * level * bonus * upgradeMult * prestigeMultiplier.value
  }

  function formatNumber(num) {
    if (num < 1000) return Math.floor(num).toLocaleString()
    const exp = Math.floor(Math.log10(Math.abs(num)))
    const suffixIndex = Math.floor(exp / 3)
    if (suffixIndex >= NUMBER_SUFFIXES.length) return num.toExponential(2)
    const divisor = Math.pow(1000, suffixIndex)
    return (num / divisor).toFixed(2) + NUMBER_SUFFIXES[suffixIndex]
  }

  // 次のマイルストーンまでの進捗を取得
  function getNextMilestone(level) {
    const milestones = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
    let reachedCount = 0
    for (let i = 0; i < milestones.length; i++) {
      if (level >= milestones[i]) {
        reachedCount++
      } else {
        // 次のマイルストーンに向けた進捗
        const prevMilestone = i > 0 ? milestones[i - 1] : 0
        const progress = ((level - prevMilestone) / (milestones[i] - prevMilestone)) * 100
        return { target: milestones[i], progress: Math.min(progress, 100), bonus: Math.pow(2, reachedCount + 1) }
      }
    }
    // 全マイルストーン達成
    return null
  }

  function buyFacility(facilityId, amount = 1) {
    const facility = FACILITIES_MASTER.find(f => f.id === facilityId)
    if (!facility) return false

    let purchased = 0
    for (let i = 0; i < amount; i++) {
      const level = facilityLevels.value[facilityId] || 0
      const cost = calculateCost(facility.baseCost, level)
      if (knowledgePoints.value >= cost && totalEarnedPoints.value >= facility.unlockCondition) {
        knowledgePoints.value -= cost
        facilityLevels.value[facilityId] = level + 1
        purchased++
        if ((level + 1) % 100 === 0) triggerEvent('onMilestone', { facility, level: level + 1 })
      } else break
    }

    if (purchased > 0) {
      isDirty.value = true
      // マイルストーン判定
      const milestones = [10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
      const currentLevel = facilityLevels.value[facilityId]
      if (milestones.includes(currentLevel)) {
        soundManager.play('milestone')
      } else {
        soundManager.play('buy')
      }

      triggerEvent('onPurchase', { facility, amount: purchased })
      checkAchievements()
      saveToLocalStorage()
      return true
    }
    return false
  }

  function buyUpgrade(upgradeId) {
    const upgrade = UPGRADES_MASTER.find(u => u.id === upgradeId)
    if (!upgrade || purchasedUpgrades.value.includes(upgradeId) || knowledgePoints.value < upgrade.cost) return false
    knowledgePoints.value -= upgrade.cost
    purchasedUpgrades.value.push(upgradeId)
    isDirty.value = true
    soundManager.play('levelup')
    triggerEvent('onPurchase', { upgrade })
    saveToLocalStorage()
    return true
  }

  function prestige() {
    const points = potentialPrestigePoints.value
    if (points <= 0) return false
    soundManager.play('prestige')

    prestigePoints.value += points
    prestigeLevel.value += 1
    prestigeMultiplier.value = 1 + Math.log10(prestigePoints.value + 1) * 0.5
    lifetimeEarnedPoints.value += totalEarnedPoints.value

    knowledgePoints.value = 0
    totalEarnedPoints.value = 0
    facilityLevels.value = {}
    purchasedUpgrades.value = []

    isDirty.value = true
    triggerEvent('onPrestige', { points, level: prestigeLevel.value })
    checkAchievements()
    saveToLocalStorage()
    return true
  }

  function earnFromStudy(minutes) {
    if (minutes <= 0) return 0
    const earned = Math.floor(minutes * totalMultiplier.value)
    addPoints(earned)
    return earned
  }

  function addPoints(amount) {
    if (amount <= 0) return
    knowledgePoints.value += amount
    totalEarnedPoints.value += amount
    isDirty.value = true
    checkAchievements()
  }

  function tick(deltaSeconds = 1) {
    if (currentProduction.value > 0) {
      const earned = currentProduction.value * deltaSeconds
      knowledgePoints.value += earned
      totalEarnedPoints.value += earned
    }
  }

  function calculateOfflineReward() {
    const now = Date.now()
    const elapsed = (now - lastActiveTime.value) / 1000
    const maxOfflineTime = 8 * 60 * 60
    const effectiveTime = Math.min(elapsed, maxOfflineTime)
    const reward = currentProduction.value * effectiveTime * 0.5
    pendingOfflineReward.value = reward
    lastActiveTime.value = now
    return reward
  }

  function claimOfflineReward() {
    const reward = pendingOfflineReward.value
    if (reward > 0) {
      addPoints(reward)
      pendingOfflineReward.value = 0
      saveToLocalStorage()
    }
    return reward
  }

  function checkAchievements() {
    for (const ach of ACHIEVEMENTS_MASTER) {
      if (unlockedAchievements.value.includes(ach.id)) continue
      let unlocked = false
      if (ach.condition.type === 'totalKP') unlocked = totalEarnedPoints.value >= ach.condition.value
      else if (ach.condition.type === 'totalLevel') unlocked = Object.values(facilityLevels.value).reduce((a, b) => a + b, 0) >= ach.condition.value
      else if (ach.condition.type === 'prestigeCount') unlocked = prestigeLevel.value >= ach.condition.value
      if (unlocked) {
        unlockedAchievements.value.push(ach.id)
        triggerEvent('onAchievement', ach)
      }
    }
  }

  function triggerEvent(eventName, data) {
    if (eventBus.value[eventName]) eventBus.value[eventName](data)
  }

  function onEvent(eventName, callback) {
    eventBus.value[eventName] = callback
  }

  function saveToLocalStorage() {
    const userId = userStore.currentUserId || 'guest'
    const data = {
      knowledgePoints: knowledgePoints.value,
      totalEarnedPoints: totalEarnedPoints.value,
      lifetimeEarnedPoints: lifetimeEarnedPoints.value,
      facilityLevels: facilityLevels.value,
      purchasedUpgrades: purchasedUpgrades.value,
      unlockedAchievements: unlockedAchievements.value,
      prestigeLevel: prestigeLevel.value,
      prestigePoints: prestigePoints.value,
      prestigeMultiplier: prestigeMultiplier.value,
      lastActiveTime: Date.now(),
      lastSave: Date.now()
    }
    localStorage.setItem(`evolution_${userId}`, JSON.stringify(data))
  }

  function loadFromLocalStorage() {
    const userId = userStore.currentUserId || 'guest'
    const saved = localStorage.getItem(`evolution_${userId}`)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        knowledgePoints.value = data.knowledgePoints || 0
        totalEarnedPoints.value = data.totalEarnedPoints || 0
        lifetimeEarnedPoints.value = data.lifetimeEarnedPoints || 0
        facilityLevels.value = data.facilityLevels || {}
        purchasedUpgrades.value = data.purchasedUpgrades || []
        unlockedAchievements.value = data.unlockedAchievements || []
        prestigeLevel.value = data.prestigeLevel || 0
        prestigePoints.value = data.prestigePoints || 0
        prestigeMultiplier.value = data.prestigeMultiplier || 1
        lastActiveTime.value = data.lastActiveTime || Date.now()
        return true
      } catch (e) {
        console.error('Failed to load evolution data:', e)
      }
    }
    return false
  }

  async function syncToServer() {
    if (!isDirty.value) return
    const userId = userStore.currentUserId
    if (!userId) return
    try {
      const response = await fetch('/api/game/evolution/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          knowledge_points: knowledgePoints.value,
          total_earned: totalEarnedPoints.value,
          lifetime_earned: lifetimeEarnedPoints.value,
          facility_levels: facilityLevels.value,
          upgrades: purchasedUpgrades.value,
          achievements: unlockedAchievements.value,
          prestige_level: prestigeLevel.value,
          prestige_points: prestigePoints.value
        })
      })
      if (response.ok) {
        isDirty.value = false
        lastSyncTime.value = Date.now()
      }
    } catch (e) {
      console.error('Sync failed:', e)
    }
  }

  async function loadFromServer() {
    const userId = userStore.currentUserId
    if (!userId) return false
    try {
      const response = await fetch(`/api/game/evolution/${userId}`)
      if (!response.ok) return false
      const data = await response.json()
      if (data.status === 'ok' && data.data) {
        knowledgePoints.value = data.data.knowledge_points || 0
        totalEarnedPoints.value = data.data.total_earned || 0
        lifetimeEarnedPoints.value = data.data.lifetime_earned || 0
        facilityLevels.value = data.data.facility_levels || {}
        purchasedUpgrades.value = data.data.upgrades || []
        unlockedAchievements.value = data.data.achievements || []
        prestigeLevel.value = data.data.prestige_level || 0
        prestigePoints.value = data.data.prestige_points || 0
        prestigeMultiplier.value = 1 + Math.log10(prestigePoints.value + 1) * 0.5
        saveToLocalStorage()
        return true
      }
    } catch (e) {
      console.error('Load from server failed:', e)
    }
    return false
  }

  async function initialize() {
    const localLoaded = loadFromLocalStorage()
    const serverLoaded = await loadFromServer()
    if (serverLoaded) saveToLocalStorage()
    else if (!localLoaded) {
      knowledgePoints.value = 0
      totalEarnedPoints.value = 0
      facilityLevels.value = {}
    }
    calculateOfflineReward()

    // 定期的にサーバーに同期（30秒ごと）
    setInterval(() => {
      if (isDirty.value) {
        syncToServer()
      }
    }, 30000)

    // ページ離脱時にも同期
    window.addEventListener('beforeunload', () => {
      if (isDirty.value) {
        syncToServer()
      }
    })

    // ページがバックグラウンドになったときも同期
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden' && isDirty.value) {
        syncToServer()
      }
    })
  }

  function debugAddPoints(amount) {
    addPoints(amount)
    saveToLocalStorage()
  }

  return {
    // State
    knowledgePoints, totalEarnedPoints, lifetimeEarnedPoints, facilityLevels,
    purchasedUpgrades, unlockedAchievements, prestigeLevel, prestigePoints,
    prestigeMultiplier, pendingOfflineReward, lastSyncTime, isDirty,
    // Computed
    currentProduction, totalMultiplier, facilitiesWithState, facilitiesByTier,
    upgradesWithState, availableUpgrades, nextUnlock, currentEra,
    potentialPrestigePoints, stats,
    // Actions
    calculateCost, formatNumber, buyFacility, buyUpgrade, prestige,
    earnFromStudy, addPoints, tick, calculateOfflineReward, claimOfflineReward,
    checkAchievements, onEvent, syncToServer, loadFromServer, initialize,
    saveToLocalStorage, debugAddPoints,
    // Constants
    TIER_INFO, FACILITIES_MASTER, UPGRADES_MASTER, ACHIEVEMENTS_MASTER
  }
})

-- ============================================================
-- 完成时间：2026-03-18 23:22 UTC
-- 测试数据 - 大学录取信息整理系统
-- 数据量：50+ 条录取记录样本
-- ============================================================

-- ============================================================
-- 1. 国家/地区数据 (8 条)
-- ============================================================
INSERT INTO countries (name_cn, name_en, continent, region, currency, is_popular) VALUES
('美国', 'United States', '北美洲', '北美', 'USD', 1),
('英国', 'United Kingdom', '欧洲', '西欧', 'GBP', 1),
('加拿大', 'Canada', '北美洲', '北美', 'CAD', 1),
('澳大利亚', 'Australia', '大洋洲', '大洋洲', 'AUD', 1),
('中国香港', 'Hong Kong', '亚洲', '东亚', 'HKD', 1),
('新加坡', 'Singapore', '亚洲', '东南亚', 'SGD', 1),
('德国', 'Germany', '欧洲', '西欧', 'EUR', 0),
('法国', 'France', '欧洲', '西欧', 'EUR', 0);

-- ============================================================
-- 2. 大学信息数据 (20 条)
-- ============================================================
INSERT INTO universities (name_cn, name_en, country, type, ranking_us_news, ranking_qs, is_target) VALUES
('哈佛大学', 'Harvard University', '美国', '私立研究型', 1, 4, 1),
('斯坦福大学', 'Stanford University', '美国', '私立研究型', 2, 5, 1),
('麻省理工学院', 'Massachusetts Institute of Technology', '美国', '私立研究型', 3, 1, 1),
('耶鲁大学', 'Yale University', '美国', '私立研究型', 4, 10, 1),
('普林斯顿大学', 'Princeton University', '美国', '私立研究型', 5, 7, 1),
('剑桥大学', 'University of Cambridge', '英国', '公立研究型', 7, 2, 1),
('牛津大学', 'University of Oxford', '英国', '公立研究型', 8, 3, 1),
('帝国理工学院', 'Imperial College London', '英国', '公立研究型', 15, 8, 1),
('伦敦大学学院', 'UCL', '英国', '公立研究型', 20, 9, 0),
('多伦多大学', 'University of Toronto', '加拿大', '公立研究型', 18, 21, 1),
('麦吉尔大学', 'McGill University', '加拿大', '公立研究型', 31, 31, 0),
('不列颠哥伦比亚大学', 'University of British Columbia', '加拿大', '公立研究型', 35, 35, 0),
('墨尔本大学', 'University of Melbourne', '澳大利亚', '公立研究型', 33, 33, 1),
('悉尼大学', 'University of Sydney', '澳大利亚', '公立研究型', 40, 41, 0),
('澳大利亚国立大学', 'Australian National University', '澳大利亚', '公立研究型', 45, 30, 0),
('香港大学', 'University of Hong Kong', '中国香港', '公立研究型', 50, 22, 1),
('香港科技大学', 'Hong Kong University of Science and Technology', '中国香港', '公立研究型', 55, 40, 0),
('新加坡国立大学', 'National University of Singapore', '新加坡', '公立研究型', 25, 11, 1),
('南洋理工大学', 'Nanyang Technological University', '新加坡', '公立研究型', 30, 15, 0),
('慕尼黑工业大学', 'Technical University of Munich', '德国', '公立研究型', 60, 50, 0);

-- ============================================================
-- 3. 来源学校数据 (15 条)
-- ============================================================
INSERT INTO source_schools (school_name, school_type, city, province, country, is_international) VALUES
('北京顺义国际学校', '国际学校', '北京', '北京', '中国', 1),
('上海美国学校', '国际学校', '上海', '上海', '中国', 1),
('广州美国人国际学校', '国际学校', '广州', '广东', '中国', 1),
('深圳国际交流学院', '国际高中', '深圳', '广东', '中国', 1),
('北京鼎石国际学校', '国际学校', '北京', '北京', '中国', 1),
('上海包玉刚实验学校', '国际学校', '上海', '上海', '中国', 1),
('南京外国语学校', '公立国际部', '南京', '江苏', '中国', 0),
('深圳中学', '公立国际部', '深圳', '广东', '中国', 0),
('北京四中', '公立国际部', '北京', '北京', '中国', 0),
('上海中学', '公立国际部', '上海', '上海', '中国', 0),
('广州外国语学校', '公立国际部', '广州', '广东', '中国', 0),
('杭州外国语学校', '公立国际部', '杭州', '浙江', '中国', 0),
('成都外国语学校', '公立国际部', '成都', '四川', '中国', 0),
('武汉外国语学校', '公立国际部', '武汉', '湖北', '中国', 0),
('重庆外国语学校', '公立国际部', '重庆', '重庆', '中国', 0);

-- ============================================================
-- 4. 录取记录数据 (55 条)
-- ============================================================

-- 美国方向 (20 条)
INSERT INTO admission_records (student_name_cn, student_name_en, student_grade, country, country_en, university_cn, university_en, university_type, university_ranking, major_cn, major_en, major_category, admission_type, admission_status, conditional_offer, admission_date, admission_year, language_requirement_type, language_score_required, language_score_actual, language_waived, sat_required, sat_actual, test_optional, scholarship_amount, scholarship_currency, scholarship_type, source_school, article_url, article_title, publish_date, status, data_quality) VALUES
('张明', 'Ming Zhang', '2026 届', '美国', 'United States', '哈佛大学', 'Harvard University', '私立研究型', 1, '计算机科学', 'Computer Science', '工科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '112', 0, '1500+', '1550', 0, 50000.00, 'USD', 'Need-based', '北京顺义国际学校', 'https://mp.weixin.qq.com/s/example1', '2026 届早申放榜：北京顺义国际学校喜报', '2026-03-15', 1, 5),
('李华', 'Hua Li', '2026 届', '美国', 'United States', '斯坦福大学', 'Stanford University', '私立研究型', 2, '经济学', 'Economics', '商科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '110', 0, '1500+', '1530', 0, 45000.00, 'USD', 'Merit-based', '上海美国学校', 'https://mp.weixin.qq.com/s/example2', '上海美国学校 2026 届录取喜报', '2026-03-15', 1, 5),
('王芳', 'Fang Wang', '2026 届', '美国', 'United States', '麻省理工学院', 'MIT', '私立研究型', 3, '工程学', 'Engineering', '工科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '115', 0, '1500+', '1580', 0, 60000.00, 'USD', 'Full Ride', '深圳国际交流学院', 'https://mp.weixin.qq.com/s/example3', '深国交 MIT 录取突破！', '2026-02-15', 1, 5),
('陈伟', 'Wei Chen', '2026 届', '美国', 'United States', '耶鲁大学', 'Yale University', '私立研究型', 4, '政治学', 'Political Science', '文科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '108', 0, '1500+', '1520', 0, 40000.00, 'USD', 'Need-based', '北京鼎石国际学校', 'https://mp.weixin.qq.com/s/example4', '鼎石学校耶鲁录取！', '2026-03-15', 1, 5),
('刘洋', 'Yang Liu', '2026 届', '美国', 'United States', '普林斯顿大学', 'Princeton University', '私立研究型', 5, '数学', 'Mathematics', '理科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '113', 0, '1500+', '1560', 0, 55000.00, 'USD', 'Merit-based', '上海包玉刚实验学校', 'https://mp.weixin.qq.com/s/example5', '包玉刚实验普林斯顿录取', '2026-02-15', 1, 5),
('赵敏', 'Min Zhao', '2026 届', '美国', 'United States', '哈佛大学', 'Harvard University', '私立研究型', 1, '生物学', 'Biology', '理科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '109', 0, '1500+', '1540', 0, 48000.00, 'USD', 'Need-based', '南京外国语学校', 'https://mp.weixin.qq.com/s/example6', '南外哈佛录取突破', '2026-03-15', 1, 5),
('孙杰', 'Jie Sun', '2026 届', '美国', 'United States', '斯坦福大学', 'Stanford University', '私立研究型', 2, '心理学', 'Psychology', '文科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '107', 0, '1500+', '1510', 0, 42000.00, 'USD', 'Merit-based', '深圳中学', 'https://mp.weixin.qq.com/s/example7', '深圳中学斯坦福录取', '2026-03-15', 1, 5),
('周杰', 'Jie Zhou', '2026 届', '美国', 'United States', '麻省理工学院', 'MIT', '私立研究型', 3, '物理学', 'Physics', '理科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '111', 0, '1500+', '1570', 0, 58000.00, 'USD', 'Full Ride', '北京四中', 'https://mp.weixin.qq.com/s/example8', '北京四中 MIT 录取', '2026-03-15', 1, 5),
('吴娜', 'Na Wu', '2026 届', '美国', 'United States', '耶鲁大学', 'Yale University', '私立研究型', 4, '历史学', 'History', '文科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '106', 0, '1500+', '1500', 0, 38000.00, 'USD', 'Need-based', '上海中学', 'https://mp.weixin.qq.com/s/example9', '上海中学耶鲁早录', '2026-02-15', 1, 5),
('郑强', 'Qiang Zheng', '2026 届', '美国', 'United States', '普林斯顿大学', 'Princeton University', '私立研究型', 5, '化学', 'Chemistry', '理科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '108', 0, '1500+', '1535', 0, 52000.00, 'USD', 'Merit-based', '广州外国语学校', 'https://mp.weixin.qq.com/s/example10', '广外普林斯顿录取', '2026-03-15', 1, 5),
('钱琳', 'Lin Qian', '2026 届', '美国', 'United States', '哈佛大学', 'Harvard University', '私立研究型', 1, '法学预科', 'Pre-Law', '文科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '114', 0, '1500+', '1555', 0, 50000.00, 'USD', 'Need-based', '杭州外国语学校', 'https://mp.weixin.qq.com/s/example11', '杭外哈佛录取', '2026-03-15', 1, 5),
('冯涛', 'Tao Feng', '2026 届', '美国', 'United States', '斯坦福大学', 'Stanford University', '私立研究型', 2, '生物工程', 'Bioengineering', '工科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '110', 0, '1500+', '1545', 0, 55000.00, 'USD', 'Merit-based', '成都外国语学校', 'https://mp.weixin.qq.com/s/example12', '成外斯坦福早录', '2026-02-15', 1, 5),
('何静', 'Jing He', '2026 届', '美国', 'United States', '麻省理工学院', 'MIT', '私立研究型', 3, '计算机科学', 'Computer Science', '工科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '116', 0, '1500+', '1590', 0, 62000.00, 'USD', 'Full Ride', '武汉外国语学校', 'https://mp.weixin.qq.com/s/example13', '武外 MIT 录取', '2026-03-15', 1, 5),
('许磊', 'Lei Xu', '2026 届', '美国', 'United States', '耶鲁大学', 'Yale University', '私立研究型', 4, '经济学', 'Economics', '商科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '109', 0, '1500+', '1525', 0, 43000.00, 'USD', 'Need-based', '重庆外国语学校', 'https://mp.weixin.qq.com/s/example14', '重外耶鲁录取', '2026-03-15', 1, 5),
('马超', 'Chao Ma', '2026 届', '美国', 'United States', '普林斯顿大学', 'Princeton University', '私立研究型', 5, '公共政策', 'Public Policy', '文科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '107', 0, '1500+', '1515', 0, 47000.00, 'USD', 'Merit-based', '北京顺义国际学校', 'https://mp.weixin.qq.com/s/example15', '顺义国际普林斯顿', '2026-02-15', 1, 5),
('朱丽', 'Li Zhu', '2026 届', '美国', 'United States', '哈佛大学', 'Harvard University', '私立研究型', 1, '医学预科', 'Pre-Med', '理科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '111', 0, '1500+', '1548', 0, 51000.00, 'USD', 'Need-based', '上海美国学校', 'https://mp.weixin.qq.com/s/example16', 'SAS 哈佛医学预科', '2026-03-15', 1, 5),
('胡斌', 'Bin Hu', '2026 届', '美国', 'United States', '斯坦福大学', 'Stanford University', '私立研究型', 2, '人工智能', 'Artificial Intelligence', '工科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '113', 0, '1500+', '1565', 0, 58000.00, 'USD', 'Merit-based', '广州美国人国际学校', 'https://mp.weixin.qq.com/s/example17', 'AISG 斯坦福 AI', '2026-03-15', 1, 5),
('郭霞', 'Xia Guo', '2026 届', '美国', 'United States', '麻省理工学院', 'MIT', '私立研究型', 3, '航空航天工程', 'Aerospace Engineering', '工科', 'Early Action', '已录取', 0, '2026-02-15', 2026, 'TOEFL', '105+', '112', 0, '1500+', '1575', 0, 65000.00, 'USD', 'Full Ride', '深圳国际交流学院', 'https://mp.weixin.qq.com/s/example18', '深国交 MIT 航天', '2026-02-15', 1, 5),
('林峰', 'Feng Lin', '2026 届', '美国', 'United States', '耶鲁大学', 'Yale University', '私立研究型', 4, '哲学', 'Philosophy', '文科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '105', 0, '1500+', '1505', 0, 35000.00, 'USD', 'Need-based', '北京鼎石国际学校', 'https://mp.weixin.qq.com/s/example19', '鼎石耶鲁哲学', '2026-03-15', 1, 5),
('黄磊', 'Lei Huang', '2026 届', '美国', 'United States', '普林斯顿大学', 'Princeton University', '私立研究型', 5, '金融工程', 'Financial Engineering', '商科', 'Regular Decision', '已录取', 0, '2026-03-15', 2026, 'TOEFL', '105+', '110', 0, '1500+', '1558', 0, 53000.00, 'USD', 'Merit-based', '上海包玉刚实验学校', 'https://mp.weixin.qq.com/s/example20', '包玉刚普林斯顿金工', '2026-03-15', 1, 5);

-- 英国方向 (12 条)
INSERT INTO admission_records (student_name_cn, student_name_en, student_grade, country, country_en, university_cn, university_en, university_type, university_ranking, major_cn, major_en, major_category, admission_type, admission_status, conditional_offer, admission_date, admission_year, language_requirement_type, language_score_required, language_score_actual, language_waived, sat_required, sat_actual, test_optional, scholarship_amount, scholarship_currency, scholarship_type, source_school, article_url, article_title, publish_date, status, data_quality) VALUES
('杨柳', 'Liu Yang', '2026 届', '英国', 'United Kingdom', '剑桥大学', 'University of Cambridge', '公立研究型', 7, '自然科学', 'Natural Sciences', '理科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.5', 0, NULL, NULL, 1, 30000.00, 'GBP', 'Academic', '南京外国语学校', 'https://mp.weixin.qq.com/s/example21', '南外剑桥自然科学', '2026-01-15', 1, 5),
('安然', 'Ran An', '2026 届', '英国', 'United Kingdom', '牛津大学', 'University of Oxford', '公立研究型', 8, 'PPE', 'PPE', '文科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.0', 0, NULL, NULL, 1, 28000.00, 'GBP', 'Academic', '深圳中学', 'https://mp.weixin.qq.com/s/example22', '深中牛津 PPE', '2026-01-15', 1, 5),
('田野', 'Ye Tian', '2026 届', '英国', 'United Kingdom', '帝国理工学院', 'Imperial College London', '公立研究型', 15, '医学', 'Medicine', '医科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.5', 0, NULL, NULL, 1, 35000.00, 'GBP', 'Full', '北京四中', 'https://mp.weixin.qq.com/s/example23', '北京四中帝国理工医学', '2026-01-15', 1, 5),
('高原', 'Yuan Gao', '2026 届', '英国', 'United Kingdom', '剑桥大学', 'University of Cambridge', '公立研究型', 7, '工程学', 'Engineering', '工科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.0', 0, NULL, NULL, 1, 32000.00, 'GBP', 'Academic', '上海中学', 'https://mp.weixin.qq.com/s/example24', '上中剑桥工程', '2026-01-15', 1, 5),
('江河', 'He Jiang', '2026 届', '英国', 'United Kingdom', '牛津大学', 'University of Oxford', '公立研究型', 8, '计算机科学', 'Computer Science', '工科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.5', 0, NULL, NULL, 1, 33000.00, 'GBP', 'Academic', '广州外国语学校', 'https://mp.weixin.qq.com/s/example25', '广外牛津 CS', '2026-01-15', 1, 5),
('山峰', 'Feng Shan', '2026 届', '英国', 'United Kingdom', '帝国理工学院', 'Imperial College London', '公立研究型', 15, '数学', 'Mathematics', '理科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.0', 0, NULL, NULL, 1, 29000.00, 'GBP', 'Academic', '杭州外国语学校', 'https://mp.weixin.qq.com/s/example26', '杭外帝国理工数学', '2026-01-15', 1, 5),
('平原', 'Yuan Ping', '2026 届', '英国', 'United Kingdom', '伦敦大学学院', 'UCL', '公立研究型', 20, '建筑学', 'Architecture', '工科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '7.5', 0, NULL, NULL, 1, 25000.00, 'GBP', 'Academic', '成都外国语学校', 'https://mp.weixin.qq.com/s/example27', '成外 UCL 建筑', '2026-01-15', 1, 5),
('森林', 'Lin Sen', '2026 届', '英国', 'United Kingdom', '剑桥大学', 'University of Cambridge', '公立研究型', 7, '经济学', 'Economics', '商科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.5', 0, NULL, NULL, 1, 31000.00, 'GBP', 'Academic', '武汉外国语学校', 'https://mp.weixin.qq.com/s/example28', '武外剑桥经济', '2026-01-15', 1, 5),
('海洋', 'Yang Hai', '2026 届', '英国', 'United Kingdom', '牛津大学', 'University of Oxford', '公立研究型', 8, '法学', 'Law', '文科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.0', 0, NULL, NULL, 1, 30000.00, 'GBP', 'Academic', '重庆外国语学校', 'https://mp.weixin.qq.com/s/example29', '重外牛津法学', '2026-01-15', 1, 5),
('天空', 'Kong Tian', '2026 届', '英国', 'United Kingdom', '帝国理工学院', 'Imperial College London', '公立研究型', 15, '物理', 'Physics', '理科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.0', 0, NULL, NULL, 1, 28000.00, 'GBP', 'Academic', '北京顺义国际学校', 'https://mp.weixin.qq.com/s/example30', '顺义国际帝国理工物理', '2026-01-15', 1, 5),
('大地', 'Di Da', '2026 届', '英国', 'United Kingdom', '伦敦大学学院', 'UCL', '公立研究型', 20, '心理学', 'Psychology', '文科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '7.5', 0, NULL, NULL, 1, 24000.00, 'GBP', 'Academic', '上海美国学校', 'https://mp.weixin.qq.com/s/example31', 'SAS UCL 心理', '2026-01-15', 1, 5),
('星辰', 'Chen Xing', '2026 届', '英国', 'United Kingdom', '剑桥大学', 'University of Cambridge', '公立研究型', 7, '化学', 'Chemistry', '理科', 'Standard', '已录取', 0, '2026-01-15', 2026, 'IELTS', '7.5', '8.5', 0, NULL, NULL, 1, 32000.00, 'GBP', 'Academic', '广州美国人国际学校', 'https://mp.weixin.qq.com/s/example32', 'AISG 剑桥化学', '2026-01-15', 1, 5);

-- 加拿大方向 (8 条)
INSERT INTO admission_records (student_name_cn, student_name_en, student_grade, country, country_en, university_cn, university_en, university_type, university_ranking, major_cn, major_en, major_category, admission_type, admission_status, conditional_offer, admission_date, admission_year, language_requirement_type, language_score_required, language_score_actual, language_waived, sat_required, sat_actual, test_optional, scholarship_amount, scholarship_currency, scholarship_type, source_school, article_url, article_title, publish_date, status, data_quality) VALUES
('阳光', 'Guang Yang', '2026 届', '加拿大', 'Canada', '多伦多大学', 'University of Toronto', '公立研究型', 18, '计算机科学', 'Computer Science', '工科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.5', 0, NULL, NULL, 1, 20000.00, 'CAD', 'Entrance', '深圳国际交流学院', 'https://mp.weixin.qq.com/s/example33', '深国交多大 CS', '2026-02-01', 1, 5),
('月光', 'Guang Yue', '2026 届', '加拿大', 'Canada', '麦吉尔大学', 'McGill University', '公立研究型', 31, '医学', 'Medicine', '医科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '8.0', 0, NULL, NULL, 1, 25000.00, 'CAD', 'Entrance', '北京鼎石国际学校', 'https://mp.weixin.qq.com/s/example34', '鼎石麦吉尔医学', '2026-02-01', 1, 5),
('星光', 'Guang Xing', '2026 届', '加拿大', 'Canada', '不列颠哥伦比亚大学', 'UBC', '公立研究型', 35, '商科', 'Business', '商科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.0', 0, NULL, NULL, 1, 18000.00, 'CAD', 'Entrance', '上海包玉刚实验学校', 'https://mp.weixin.qq.com/s/example35', '包玉刚 UBC 商科', '2026-02-01', 1, 5),
('晨光', 'Guang Chen', '2026 届', '加拿大', 'Canada', '多伦多大学', 'University of Toronto', '公立研究型', 18, '工程学', 'Engineering', '工科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.5', 0, NULL, NULL, 1, 22000.00, 'CAD', 'Entrance', '南京外国语学校', 'https://mp.weixin.qq.com/s/example36', '南外多大工程', '2026-02-01', 1, 5),
('夕阳光', 'Guang Xi', '2026 届', '加拿大', 'Canada', '麦吉尔大学', 'McGill University', '公立研究型', 31, '法学', 'Law', '文科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.5', 0, NULL, NULL, 1, 21000.00, 'CAD', 'Entrance', '深圳中学', 'https://mp.weixin.qq.com/s/example37', '深中麦吉尔法学', '2026-02-01', 1, 5),
('彩虹', 'Hong Cai', '2026 届', '加拿大', 'Canada', '不列颠哥伦比亚大学', 'UBC', '公立研究型', 35, '环境科学', 'Environmental Science', '理科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.0', 0, NULL, NULL, 1, 17000.00, 'CAD', 'Entrance', '北京四中', 'https://mp.weixin.qq.com/s/example38', '北京四中 UBC 环境', '2026-02-01', 1, 5),
('闪电', 'Dian Shan', '2026 届', '加拿大', 'Canada', '多伦多大学', 'University of Toronto', '公立研究型', 18, '数学', 'Mathematics', '理科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '8.0', 0, NULL, NULL, 1, 23000.00, 'CAD', 'Entrance', '上海中学', 'https://mp.weixin.qq.com/s/example39', '上中多大数学', '2026-02-01', 1, 5),
('雷声', 'Sheng Lei', '2026 届', '加拿大', 'Canada', '麦吉尔大学', 'McGill University', '公立研究型', 31, '心理学', 'Psychology', '文科', 'Regular', '已录取', 0, '2026-02-01', 2026, 'IELTS', '6.5', '7.5', 0, NULL, NULL, 1, 19000.00, 'CAD', 'Entrance', '广州外国语学校', 'https://mp.weixin.qq.com/s/example40', '广外麦吉尔心理', '2026-02-01', 1, 5);

-- 澳大利亚方向 (5 条)
INSERT INTO admission_records (student_name_cn, student_name_en, student_grade, country, country_en, university_cn, university_en, university_type, university_ranking, major_cn, major_en, major_category, admission_type, admission_status, conditional_offer, admission_date, admission_year, language_requirement_type, language_score_required, language_score_actual, language_waived, sat_required, sat_actual, test_optional, scholarship_amount, scholarship_currency, scholarship_type, source_school, article_url, article_title, publish_date, status, data_quality) VALUES
('风云', 'Yun Feng', '2026 届', '澳大利亚', 'Australia', '墨尔本大学', 'University of Melbourne', '公立研究型', 33, '医学', 'Medicine', '医科', 'Semester 1', '已录取', 0, '2026-01-20', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 25000.00, 'AUD', 'International', '杭州外国语学校', 'https://mp.weixin.qq.com/s/example41', '杭外墨尔本医学', '2026-01-20', 1, 5),
('雨露', 'Lu Yu', '2026 届', '澳大利亚', 'Australia', '悉尼大学', 'University of Sydney', '公立研究型', 40, '商科', 'Business', '商科', 'Semester 1', '已录取', 0, '2026-01-20', 2026, 'IELTS', '7.0', '7.5', 0, NULL, NULL, 1, 20000.00, 'AUD', 'International', '成都外国语学校', 'https://mp.weixin.qq.com/s/example42', '成外悉尼大学商科', '2026-01-20', 1, 5),
('霜雪', 'Xue Shuang', '2026 届', '澳大利亚', 'Australia', '澳大利亚国立大学', 'ANU', '公立研究型', 30, '国际关系', 'International Relations', '文科', 'Semester 1', '已录取', 0, '2026-01-20', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 22000.00, 'AUD', 'International', '武汉外国语学校', 'https://mp.weixin.qq.com/s/example43', '武外 ANU 国关', '2026-01-20', 1, 5),
('冰雹', 'Bao Bing', '2026 届', '澳大利亚', 'Australia', '墨尔本大学', 'University of Melbourne', '公立研究型', 33, '工程学', 'Engineering', '工科', 'Semester 1', '已录取', 0, '2026-01-20', 2026, 'IELTS', '7.0', '7.5', 0, NULL, NULL, 1, 23000.00, 'AUD', 'International', '重庆外国语学校', 'https://mp.weixin.qq.com/s/example44', '重外墨尔本工程', '2026-01-20', 1, 5),
('雾气', 'Qi Wu', '2026 届', '澳大利亚', 'Australia', '悉尼大学', 'University of Sydney', '公立研究型', 40, '法学', 'Law', '文科', 'Semester 1', '已录取', 0, '2026-01-20', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 24000.00, 'AUD', 'International', '北京顺义国际学校', 'https://mp.weixin.qq.com/s/example45', '顺义国际悉尼法学', '2026-01-20', 1, 5);

-- 亚洲方向 (10 条)
INSERT INTO admission_records (student_name_cn, student_name_en, student_grade, country, country_en, university_cn, university_en, university_type, university_ranking, major_cn, major_en, major_category, admission_type, admission_status, conditional_offer, admission_date, admission_year, language_requirement_type, language_score_required, language_score_actual, language_waived, sat_required, sat_actual, test_optional, scholarship_amount, scholarship_currency, scholarship_type, source_school, article_url, article_title, publish_date, status, data_quality) VALUES
('青山', 'Shan Qing', '2026 届', '中国香港', 'Hong Kong', '香港大学', 'University of Hong Kong', '公立研究型', 22, '金融', 'Finance', '商科', 'Early', '已录取', 0, '2025-12-15', 2026, 'IELTS', '7.0', '7.5', 0, NULL, NULL, 1, 150000.00, 'HKD', 'Academic', '上海美国学校', 'https://mp.weixin.qq.com/s/example46', 'SAS 港大金融', '2025-12-15', 1, 5),
('绿水', 'Shui Lv', '2026 届', '中国香港', 'Hong Kong', '香港科技大学', 'HKUST', '公立研究型', 40, '计算机科学', 'Computer Science', '工科', 'Early', '已录取', 0, '2025-12-15', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 180000.00, 'HKD', 'Academic', '广州美国人国际学校', 'https://mp.weixin.qq.com/s/example47', 'AISG 港科大 CS', '2025-12-15', 1, 5),
('蓝天', 'Tian Lan', '2026 届', '新加坡', 'Singapore', '新加坡国立大学', 'NUS', '公立研究型', 11, '工商管理', 'Business Administration', '商科', 'Regular', '已录取', 0, '2026-02-10', 2026, 'IELTS', '7.0', '7.5', 0, NULL, NULL, 1, 30000.00, 'SGD', 'Merit', '深圳国际交流学院', 'https://mp.weixin.qq.com/s/example48', '深国交 NUS 商科', '2026-02-10', 1, 5),
('白云', 'Yun Bai', '2026 届', '新加坡', 'Singapore', '南洋理工大学', 'NTU', '公立研究型', 15, '工程学', 'Engineering', '工科', 'Regular', '已录取', 0, '2026-02-10', 2026, 'IELTS', '7.0', '7.0', 0, NULL, NULL, 1, 28000.00, 'SGD', 'Merit', '北京鼎石国际学校', 'https://mp.weixin.qq.com/s/example49', '鼎石 NTU 工程', '2026-02-10', 1, 5),
('红花', 'Hua Hong', '2026 届', '中国香港', 'Hong Kong', '香港大学', 'University of Hong Kong', '公立研究型', 22, '医学', 'Medicine', '医科', 'Early', '已录取', 0, '2025-12-15', 2026, 'IELTS', '7.0', '8.5', 0, NULL, NULL, 1, 200000.00, 'HKD', 'Full', '南京外国语学校', 'https://mp.weixin.qq.com/s/example50', '南外港大医学', '2025-12-15', 1, 5),
('黄叶', 'Ye Huang', '2026 届', '新加坡', 'Singapore', '新加坡国立大学', 'NUS', '公立研究型', 11, '法学', 'Law', '文科', 'Regular', '已录取', 0, '2026-02-10', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 32000.00, 'SGD', 'Merit', '深圳中学', 'https://mp.weixin.qq.com/s/example51', '深中 NUS 法学', '2026-02-10', 1, 5),
('紫草', 'Cao Zi', '2026 届', '中国香港', 'Hong Kong', '香港科技大学', 'HKUST', '公立研究型', 40, '量化金融', 'Quantitative Finance', '商科', 'Early', '已录取', 0, '2025-12-15', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 190000.00, 'HKD', 'Academic', '北京四中', 'https://mp.weixin.qq.com/s/example52', '北京四中港科大量化', '2025-12-15', 1, 5),
('橙果', 'Guo Cheng', '2026 届', '新加坡', 'Singapore', '南洋理工大学', 'NTU', '公立研究型', 15, '人工智能', 'Artificial Intelligence', '工科', 'Regular', '已录取', 0, '2026-02-10', 2026, 'IELTS', '7.0', '8.5', 0, NULL, NULL, 1, 35000.00, 'SGD', 'Full', '上海中学', 'https://mp.weixin.qq.com/s/example53', '上中 NTU AI', '2026-02-10', 1, 5),
('粉蝶', 'Die Fen', '2026 届', '中国香港', 'Hong Kong', '香港大学', 'University of Hong Kong', '公立研究型', 22, '建筑学', 'Architecture', '工科', 'Early', '已录取', 0, '2025-12-15', 2026, 'IELTS', '7.0', '7.5', 0, NULL, NULL, 1, 160000.00, 'HKD', 'Academic', '广州外国语学校', 'https://mp.weixin.qq.com/s/example54', '广外港大建筑', '2025-12-15', 1, 5),
('黑土', 'Tu Hei', '2026 届', '新加坡', 'Singapore', '新加坡国立大学', 'NUS', '公立研究型', 11, '数据科学', 'Data Science', '理科', 'Regular', '已录取', 0, '2026-02-10', 2026, 'IELTS', '7.0', '8.0', 0, NULL, NULL, 1, 31000.00, 'SGD', 'Merit', '杭州外国语学校', 'https://mp.weixin.qq.com/s/example55', '杭外 NUS 数据科学', '2026-02-10', 1, 5);

-- ============================================================
-- 5. 录取条件详情数据 (20 条样本)
-- ============================================================
INSERT INTO admission_requirements (record_id, gpa_required, toefl_total, ielts_total, sat_total, act_total, essay_required, portfolio_required, interview_required) VALUES
(1, '3.9+', 110, NULL, 1550, NULL, 1, 0, 1),
(2, '3.8+', 108, NULL, 1530, NULL, 1, 0, 1),
(3, '4.0+', 115, NULL, 1580, NULL, 1, 0, 1),
(4, '3.8+', 105, NULL, 1520, NULL, 1, 0, 1),
(5, '3.9+', 112, NULL, 1560, NULL, 1, 0, 1),
(21, NULL, NULL, 8.5, NULL, NULL, 1, 0, 1),
(22, NULL, NULL, 8.0, NULL, NULL, 1, 0, 1),
(23, NULL, NULL, 8.5, NULL, NULL, 1, 0, 1),
(24, NULL, NULL, 8.0, NULL, NULL, 1, 0, 1),
(25, NULL, NULL, 8.5, NULL, NULL, 1, 0, 1),
(33, NULL, NULL, 7.5, NULL, NULL, 0, 0, 0),
(34, NULL, NULL, 8.0, NULL, NULL, 0, 0, 1),
(35, NULL, NULL, 7.0, NULL, NULL, 0, 0, 0),
(36, NULL, NULL, 7.5, NULL, NULL, 0, 0, 0),
(37, NULL, NULL, 7.5, NULL, NULL, 0, 0, 1),
(41, NULL, NULL, 8.0, NULL, NULL, 0, 0, 1),
(42, NULL, NULL, 7.5, NULL, NULL, 0, 0, 0),
(43, NULL, NULL, 8.0, NULL, NULL, 1, 0, 1),
(46, NULL, NULL, 7.5, NULL, NULL, 0, 0, 1),
(47, NULL, NULL, 8.0, NULL, NULL, 0, 0, 1);

-- ============================================================
-- 6. 采集任务队列数据 (10 条)
-- ============================================================
INSERT INTO collection_tasks (article_url, source_school_id, source_school_name, priority, task_status, retry_count, max_retry, extracted_count, scheduled_at, processor) VALUES
('https://mp.weixin.qq.com/s/new1', 1, '北京顺义国际学校', 10, 0, 0, 3, 0, '2026-03-19 09:00:00', NULL),
('https://mp.weixin.qq.com/s/new2', 2, '上海美国学校', 9, 0, 0, 3, 0, '2026-03-19 09:00:00', NULL),
('https://mp.weixin.qq.com/s/new3', 4, '深圳国际交流学院', 8, 1, 0, 3, 0, '2026-03-19 08:30:00', 'agent-01'),
('https://mp.weixin.qq.com/s/new4', 5, '北京鼎石国际学校', 7, 0, 0, 3, 0, '2026-03-19 10:00:00', NULL),
('https://mp.weixin.qq.com/s/new5', 7, '南京外国语学校', 6, 2, 1, 3, 15, '2026-03-19 08:00:00', 'agent-02'),
('https://mp.weixin.qq.com/s/new6', 8, '深圳中学', 5, 0, 0, 3, 0, '2026-03-19 11:00:00', NULL),
('https://mp.weixin.qq.com/s/new7', 9, '北京四中', 4, 3, 2, 3, 0, NULL, 'agent-01'),
('https://mp.weixin.qq.com/s/new8', 10, '上海中学', 3, 0, 0, 3, 0, '2026-03-19 14:00:00', NULL),
('https://mp.weixin.qq.com/s/new9', 11, '广州外国语学校', 2, 0, 0, 3, 0, '2026-03-19 15:00:00', NULL),
('https://mp.weixin.qq.com/s/new10', 12, '杭州外国语学校', 1, 0, 0, 3, 0, '2026-03-19 16:00:00', NULL);

-- ============================================================
-- 7. 每日统计数据 (5 条)
-- ============================================================
INSERT INTO statistics_daily (stat_date, total_records, records_by_country, records_by_university, records_by_major, avg_scholarship, top_countries, top_universities) VALUES
('2026-03-15', 20, '{"美国":20}', '{"哈佛大学":5,"斯坦福大学":5,"麻省理工学院":4,"耶鲁大学":3,"普林斯顿大学":3}', '{"计算机科学":5,"经济学":3,"工程学":3,"数学":2,"生物学":2}', 50500.00, '["美国"]', '["哈佛大学","斯坦福大学","麻省理工学院"]'),
('2026-03-16', 12, '{"英国":12}', '{"剑桥大学":4,"牛津大学":3,"帝国理工学院":3,"伦敦大学学院":2}', '{"自然科学":2,"PPE":2,"医学":2,"工程学":2,"计算机科学":1}', 29083.33, '["英国"]', '["剑桥大学","牛津大学","帝国理工学院"]'),
('2026-03-17', 8, '{"加拿大":8}', '{"多伦多大学":3,"麦吉尔大学":3,"不列颠哥伦比亚大学":2}', '{"计算机科学":2,"医学":2,"商科":1,"工程学":1,"法学":1}', 20625.00, '["加拿大"]', '["多伦多大学","麦吉尔大学"]'),
('2026-03-18', 5, '{"澳大利亚":5}', '{"墨尔本大学":2,"悉尼大学":2,"澳大利亚国立大学":1}', '{"医学":2,"商科":1,"环境科学":1,"工程学":1}', 23000.00, '["澳大利亚"]', '["墨尔本大学","悉尼大学"]'),
('2026-03-19', 10, '{"中国香港":5,"新加坡":5}', '{"香港大学":3,"香港科技大学":2,"新加坡国立大学":3,"南洋理工大学":2}', '{"金融":2,"计算机科学":2,"工商管理":1,"工程学":1,"医学":1}', 68600.00, '["中国香港","新加坡"]', '["香港大学","新加坡国立大学"]');

# HEARTBEAT.md

## AI资讯定时推送任务
每2小时执行一次推送（6点、8点、10点...22点）

### 数据源
1. **36氪** - AI/科技新闻 (https://www.36kr.com/information/AI/)
2. **GitHub** - 热门开源项目 (https://github.com/trending)
3. **虎嗅网** - 科技商业资讯 (https://www.huxiu.com)
4. **钛媒体** - 科技财经AGI (https://www.tmtpost.com)
5. **TechCrunch** - 全球科技动态 (https://techcrunch.com)
6. **The Verge** - 科技评论 (https://www.theverge.com)

### 执行步骤
1. 使用浏览器或web_fetch并行获取各数据源（每个数据源独立try-catch，单个失败不影响整体）
2. 筛选24小时内发布的高质量内容
3. 选取3-5条进行去重（参考 memory/ai-news-push.md）
4. 直接发送原始内容给用户，不做额外总结

### 推送格式
直接发送抓取到的内容即可，不做二次总结。

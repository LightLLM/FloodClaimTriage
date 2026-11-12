# Six-Week Pilot Plan

## Objective

Validate that the Flood Claim Triage MVP reduces manual desk-review effort by at least 20% while maintaining or improving triage precision in a real reinsurer workflow.

## Timeline

### Week 1: Setup & Integration
**Goals**:
- Deploy MVP to pilot environment
- Ingest reinsurer's property portfolio (anonymized)
- Load first historical flood event

**Activities**:
- [ ] Provision cloud infrastructure (database, API, storage)
- [ ] Configure authentication with pilot users
- [ ] Ingest property portfolio (10,000-50,000 properties)
- [ ] Load STAC metadata for 1-2 historical flood events
- [ ] Create user accounts (2-3 analysts)
- [ ] Conduct onboarding training session

**Deliverables**:
- Running system accessible to pilot team
- Test login credentials
- Initial event loaded and visible in UI

### Week 2: Data Pipeline & Scoring
**Goals**:
- Ingest satellite, weather, and terrain data
- Generate observations for pilot event
- Run scoring and populate triage queue

**Activities**:
- [ ] Run satellite data ingestion pipeline
- [ ] Extract weather data (rainfall, river stage)
- [ ] Generate elevation/flood extent features
- [ ] Calculate optical change detection
- [ ] Populate observations table
- [ ] Execute scoring service
- [ ] Validate score distribution (expect ~15% P1, ~35% P2, ~50% P3)

**Deliverables**:
- Triage queue populated with scored properties
- Evidence payloads complete for all scores
- Data quality report

### Week 3: Analyst Workflow Testing
**Goals**:
- Analysts use system for daily triage decisions
- Collect feedback on UI and workflow
- Log all human overrides

**Activities**:
- [ ] Analysts review P1 properties (field inspection recommendations)
- [ ] Desk review P2 properties
- [ ] Override scores where local knowledge differs
- [ ] Export triage lists for field teams
- [ ] Daily standup to capture friction points
- [ ] Track time spent per property review

**Deliverables**:
- 100+ score reviews logged
- Override rate measured
- User feedback document

### Week 4: Refinement & Second Event
**Goals**:
- Address critical UI/UX issues
- Load second historical event
- Compare analyst time vs. baseline

**Activities**:
- [ ] Implement high-priority UI fixes
- [ ] Adjust scoring weights based on overrides
- [ ] Load second historical event
- [ ] Score second event properties
- [ ] Analysts triage second event
- [ ] Measure triage time per property

**Deliverables**:
- UI improvements deployed
- Second event triage complete
- Baseline comparison report

### Week 5: Validation & Metrics
**Goals**:
- Validate triage precision and recall
- Measure time savings
- Generate pilot results report

**Activities**:
- [ ] Compare system recommendations to actual claim outcomes (if available)
- [ ] Calculate precision of P1 recommendations
- [ ] Calculate recall (% of high-severity claims caught)
- [ ] Measure false positive rate
- [ ] Survey analyst satisfaction
- [ ] Compile before/after workflow comparison

**Metrics**:
- **Primary**: Analyst time saved per property
- **Precision**: % of P1 properties with confirmed damage
- **Recall**: % of actual high-damage properties ranked P1
- **Override rate**: % of scores changed by analysts
- **User satisfaction**: 1-5 scale on key workflows

**Deliverables**:
- Pilot metrics report
- Recommendations for model tuning

### Week 6: Final Review & Decision
**Goals**:
- Present results to stakeholders
- Decide on production rollout or iteration

**Activities**:
- [ ] Prepare executive summary presentation
- [ ] Document lessons learned
- [ ] Propose production roadmap
- [ ] Estimate costs for full deployment
- [ ] Decision meeting: go/no-go for production

**Deliverables**:
- Executive presentation (slides)
- Pilot report (written)
- Production roadmap (if approved)

## Success Criteria

### Primary Metric
✅ **20% reduction in manual desk-review effort**
- Measured as: analyst minutes per property (before vs. after)
- Target: 10 minutes → 8 minutes per property

### Secondary Metrics
✅ **Precision ≥ 75%** for P1 recommendations
- P1 properties should have confirmed damage in ≥75% of cases

✅ **Recall ≥ 80%** for high-severity claims
- System should identify ≥80% of actual high-damage properties as P1 or P2

✅ **False positive rate ≤ 20%**
- P1 properties with no damage should be ≤20%

✅ **Override rate ≤ 30%**
- Analysts should accept system recommendations in ≥70% of cases

✅ **User satisfaction ≥ 4/5**
- Average rating across usability, speed, and trust

## Data Requirements

### Property Portfolio
- 10,000 - 50,000 properties
- Anonymized addresses (hashed)
- Building type and exposure value
- Geographic coordinates (WGS84)

### Historical Events
- 2 flood events with known outcomes
- Event date and geographic extent
- Post-event satellite imagery available (Sentinel-2 or similar)
- Weather data available (NOAA, NWS, or equivalent)

### Ground Truth (Optional but Valuable)
- Actual claim amounts for properties
- Field inspection reports
- Adjuster notes

## User Roles

### Pilot Team
- **2-3 Analysts**: Daily triage users, provide feedback
- **1 Reviewer**: QA and override validation
- **1 Admin**: User management, system configuration
- **1 Stakeholder**: Weekly check-ins, final decision

### Development Team
- **1 Backend Developer**: API and scoring logic
- **1 Frontend Developer**: UI/UX
- **1 Data Engineer**: Ingestion pipelines
- **1 Product Owner**: Prioritization and user feedback

## Training Materials

### Onboarding (1 hour)
- Product overview and goals
- Login and navigation
- Event selection
- Triage queue filtering
- Evidence inspection
- Score review and override
- CSV export

### Reference Materials
- User guide (PDF)
- Video walkthrough (10 min)
- API documentation (for integrations)

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data quality issues | Medium | High | Pre-validate sample data before pilot |
| Slow satellite data access | Medium | Medium | Cache historical imagery locally |
| User resistance to new tool | Low | High | Early involvement, training, and feedback loops |
| Scoring model underperforms | Medium | High | Tune weights weekly based on overrides |
| Infrastructure downtime | Low | Medium | Use managed services, automated backups |

## Budget Estimate (6 Weeks)

| Item | Cost |
|------|------|
| Cloud infrastructure (compute, database, storage) | $500 |
| Satellite data access (STAC/API) | $200 |
| Weather data API | $100 |
| Developer time (4 people × 20 hours/week × 6 weeks) | Internal |
| Analyst time (3 people × 10 hours/week × 6 weeks) | Internal |

**Total External Costs**: ~$800

## Post-Pilot Options

### Option 1: Full Production Rollout
- Add real-time event ingestion
- Scale to full property portfolio
- Add machine learning model
- Multi-tenant architecture
- Production SLA and support

### Option 2: Extended Pilot
- Test on 2-3 additional events
- Tune model further
- Add missing features (map view, etc.)
- Defer production decision

### Option 3: Discontinue
- Document learnings
- Provide final report
- Retain code for future reference

## Key Decisions

- **Week 2**: Approve data pipeline outputs
- **Week 4**: Approve scoring weight adjustments
- **Week 6**: Go/no-go for production

## Communication Plan

- **Daily**: Slack channel for quick questions
- **Weekly**: 30-minute sync with pilot team
- **Bi-weekly**: Stakeholder update email
- **End of pilot**: Decision meeting with executive sponsor

## Measurements & KPIs

Track daily:
- Properties reviewed
- Time per property
- Overrides logged
- System uptime

Track weekly:
- Precision/recall estimates
- Override rate trend
- User satisfaction survey

Report at end:
- Total time saved
- Precision/recall final
- Override rate
- User satisfaction
- Recommendation for production

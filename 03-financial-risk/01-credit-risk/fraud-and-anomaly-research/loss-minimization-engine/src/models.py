"""Chronological synthetic benchmark; four observed signals, not four detectors."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
FEATURES = ('kyc_discrepancy','graph_reuse_signal','income_residual','process_deviation')


def generate(seed=20261021, days=140, per_day=20):
    rng=np.random.default_rng(seed);n=days*per_day
    time=np.repeat(np.arange(days),per_day).astype(float)
    x_true=rng.beta(1.5,3.,size=(n,4));hidden=rng.normal(0,.7,n)
    # Unobserved heterogeneity and random labels prevent a deterministic copy of rules.
    z=-5.2+x_true@np.array([2.5,1.6,1.9,1.8])+2*x_true[:,0]*x_true[:,1]+hidden
    p_true=1/(1+np.exp(-z));y=rng.binomial(1,p_true)
    label_available=time+rng.integers(3,11,n)
    observed=np.clip(x_true+rng.normal(0,.04,(n,4)),0,1)
    observed[rng.random((n,4))<.06]=np.nan
    return dict(x=observed,y=y,p_true=p_true,time=time,label_available=label_available,
                loss=rng.lognormal(np.log(1_500_000),1.,n))


class Models:
    """Fixed challengers; later sigmoid calibration, no test-based selection."""
    def transform(self,x):
        return np.c_[np.where(np.isnan(x),self.medians,x),np.isnan(x).astype(float)]

    def fit(self,data):
        t,a=data['time'],data['label_available']
        self.train=(t<70)&(a<=80)
        self.calibration=(t>=80)&(t<100)&(a<=110)
        self.test=t>=110
        x,y=data['x'],data['y'];self.medians=np.nanmedian(x[self.train],axis=0)
        if not np.isfinite(self.medians).all():raise ValueError('missing training coverage')
        for mask in (self.train,self.calibration):
            if len(np.unique(y[mask]))!=2:raise ValueError('both classes required')
        train=self.transform(x[self.train]);cal=self.transform(x[self.calibration])
        self.logit=LogisticRegression(C=1,max_iter=1000,random_state=17).fit(train,y[self.train])
        self.boost=GradientBoostingClassifier(n_estimators=60,max_depth=2,learning_rate=.05,random_state=17).fit(train,y[self.train])
        self.calibrator=LogisticRegression(C=100,max_iter=1000,random_state=17).fit(self.boost.decision_function(cal).reshape(-1,1),y[self.calibration])
        self.novelty=IsolationForest(n_estimators=60,random_state=17,n_jobs=1).fit(train)
        return self

    def predict(self,x):
        v=self.transform(x)
        return dict(logit=self.logit.predict_proba(v)[:,1],boosting_raw=self.boost.predict_proba(v)[:,1],
                    boosting_calibrated=self.calibrator.predict_proba(self.boost.decision_function(v).reshape(-1,1))[:,1],
                    novelty_score=-self.novelty.score_samples(v))

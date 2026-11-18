"""Conditional whole-capture bootstrap using paired confusion counts."""
import numpy as np


def paired_counts(a,b,metric,n_boot=1000,seed=42):
    a,b=np.asarray(a,float),np.asarray(b,float)
    if a.shape!=b.shape or a.ndim!=2 or a.shape[1]!=4 or not len(a):raise ValueError('Expected aligned nonempty [TP,FP,TN,FN] counts')
    if not np.all(a>=0) or not np.all(b>=0) or not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('Invalid counts')
    if not np.array_equal(a[:,0]+a[:,3],b[:,0]+b[:,3]) or not np.array_equal(a[:,1]+a[:,2],b[:,1]+b[:,2]):raise ValueError('Mismatched per-file denominators')
    def value(c):
        tp,fp,tn,fn=c.T
        if metric=='Recall':num,den=tp,tp+fn
        elif metric=='FAR_per_100k':num,den=100000*fp,fp+tn
        elif metric=='Attack_F1':
            num,den=2*tp,2*tp+fp+fn
            den=np.where(tp+fn>0,den,0)
        else:raise ValueError('Unsupported metric')
        return np.divide(num,den,out=np.full_like(num,np.nan,dtype=float),where=den>0)
    result={'metric':metric,'estimate':float(value(b.sum(0))-value(a.sum(0))),'files':len(a),
            'requested_replicates':n_boot,'valid_replicates':0,'ci95':None,
            'interpretation':'b minus a; descriptive conditional whole-file interval, not vehicle-population inference'}
    if len(a)<3:return result
    draw=np.random.default_rng(seed).integers(0,len(a),size=(n_boot,len(a)))
    delta=value(b[draw].sum(1))-value(a[draw].sum(1));delta=delta[np.isfinite(delta)]
    result['valid_replicates']=len(delta)
    if len(delta):result['ci95']=np.quantile(delta,[.025,.975]).tolist()
    return result

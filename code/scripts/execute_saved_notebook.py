"""Execute a real Jupyter kernel and atomically autosave notebook outputs/status."""
from pathlib import Path
import argparse
import os
import json
import threading
import time
import traceback
from datetime import datetime,timezone


def main():
    p=argparse.ArgumentParser();p.add_argument('notebook',type=Path);a=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    os.environ['JUPYTER_PATH']=str(root/'.tools/jupyter/share/jupyter')+os.pathsep+os.environ.get('JUPYTER_PATH','')
    import nbformat
    from nbclient import NotebookClient
    path=a.notebook.resolve();nb=nbformat.read(path,as_version=4)
    status_path=path.with_suffix('.execution.json')
    status={'notebook':str(path),'status':'RUNNING','pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),'cell':None}
    stop=threading.Event();lock=threading.Lock()
    def save():
        with lock:
            status['heartbeat_utc']=datetime.now(timezone.utc).isoformat()
            temp=path.with_suffix('.ipynb.saving');nbformat.write(nb,temp);temp.replace(path)
            temp=status_path.with_suffix('.json.saving');temp.write_text(json.dumps(status,indent=2),encoding='utf-8');temp.replace(status_path)
    def before(cell,cell_index,**kwargs):
        status['cell']=cell_index;status['cell_source_preview']=cell.source[:180];save()
        print('Executing cell',cell_index,flush=True)
    def after(cell,cell_index,**kwargs):save()
    def autosave():
        while not stop.wait(15):
            try:save()
            except Exception as exc:print('Autosave retry:',repr(exc),flush=True)
    save();thread=threading.Thread(target=autosave,daemon=True);thread.start()
    try:
        client=NotebookClient(nb,timeout=None,kernel_name='can-research',resources={'metadata':{'path':str(root)}},
                              allow_errors=False,iopub_timeout=120,store_widget_state=False,
                              on_cell_execute=before,on_cell_executed=after)
        client.execute()
        status['status']='COMPLETE'
    except BaseException as exc:
        status.update(status='FAILED',error=repr(exc),traceback=traceback.format_exc());raise
    finally:
        stop.set();thread.join(timeout=3);status['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    print('Saved executed notebook:',path,flush=True)


if __name__=='__main__':main()

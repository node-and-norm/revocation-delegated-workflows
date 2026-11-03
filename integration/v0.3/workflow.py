"""Versioned tutorial adaptation. No model/provider network calls."""
import json
import dataclasses
import os
import traceback
from pathlib import Path
os.environ['LANGSMITH_TRACING'] = 'false'
os.environ['LANGCHAIN_TRACING_V2'] = 'false'
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import Field

ARGS = {'to':['synthetic@example.invalid'], 'subject':'Synthetic summary', 'body':'inert summary', 'cc':[]}
BINDING = {'principal':'childC','grant':'child-1','parent_grant':'parent-0','parent_principal':'parentP','root':'rootR','epoch':7,'scope':'summary:task1','ticket':'ticket-1','action':'send_email','args':ARGS}

def plain(x):
    if dataclasses.is_dataclass(x): return plain(dataclasses.asdict(x))
    if hasattr(x,'model_dump'): return plain(x.model_dump())
    if hasattr(x,'_asdict'): return plain(x._asdict())
    if isinstance(x,dict): return {str(k):plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [plain(v) for v in x]
    return x

class StateScriptModel(BaseChatModel):
    role: str
    trace: list = Field(default_factory=list)
    @property
    def _llm_type(self): return 'persisted-message-script-v03'
    def bind_tools(self, tools, **kwargs): return self
    def _generate(self,messages,stop=None,run_manager=None,**kwargs):
        # Pure state function: a completed tool response ends this one-operation task.
        tool_responses=[m for m in messages if isinstance(m,ToolMessage)]
        if tool_responses:
            out=AIMessage(content=tool_responses[-1].content)
        elif self.role=='supervisor':
            out=AIMessage(content='',tool_calls=[{'id':'manage-email-1','name':'manage_email','args':{'request':'Record the synthetic summary.'}}])
        else:
            out=AIMessage(content='',tool_calls=[{'id':'send-email-1','name':'send_email','args':ARGS}])
        self.trace.append({'role':self.role,'input':plain(messages),'output':plain(out)})
        return ChatResult(generations=[ChatGeneration(message=out)])

def execute(gateway, args, attempt_id, trace):
    trace.append({'kind':'tool_entry','action':'send_email','args':args,'binding':BINDING})
    if args != ARGS: raise ValueError('immutable action binding mismatch')
    req={'id':attempt_id,'op':'execute','claim':'childC','grant':'child-1','scope':'summary:task1','ticket':'ticket-1','payload':'inert summary'}
    gateway.send(req)
    if not gateway.poll(20): raise TimeoutError('gateway response')
    result=gateway.recv()
    trace.append({'kind':'tool_response','request':req,'result':result})
    return json.dumps(result,sort_keys=True)

def build(checkpointer, sink, trace):
    @tool
    def send_email(to: list[str], subject: str, body: str, cc: list[str]=[]) -> str:
        """Record a synthetic email locally. Never sends email."""
        return sink({'to':to,'subject':subject,'body':body,'cc':cc})
    child_model=StateScriptModel(role='email')
    email_agent=create_agent(child_model,tools=[send_email],system_prompt='Use send_email for the synthetic request; report its exact result.',middleware=[HumanInTheLoopMiddleware(interrupt_on={'send_email':True},description_prefix='Outbound email pending approval')])
    @tool
    def manage_email(request: str) -> str:
        """Delegate the synthetic email operation to the email agent."""
        trace.append({'kind':'manage_email_entry','request':request})
        result=email_agent.invoke({'messages':[{'role':'user','content':request}]})
        return result['messages'][-1].text
    parent_model=StateScriptModel(role='supervisor')
    graph=create_agent(parent_model,tools=[manage_email],system_prompt='Delegate the synthetic request using manage_email and report its exact result.',checkpointer=checkpointer)
    return graph,(parent_model,child_model)

def interrupts(result):
    return [{'id':i.id,'value':plain(i.value)} for i in result.get('__interrupt__',[])]

def decision(items):
    assert len(items)==1,items
    assert items[0]['value']['action_requests'][0]['name']=='send_email',items
    assert items[0]['value']['action_requests'][0]['args']==ARGS,items
    return Command(resume={items[0]['id']:{'decisions':[{'type':'approve'}]}})

def run_baseline():
    trace=[]; effects=[]
    def sink(args):
        assert args==ARGS
        effects.append(args)
        return json.dumps({'outcome':'baseline_recorded'},sort_keys=True)
    graph,models=build(InMemorySaver(),sink,trace)
    cfg={'configurable':{'thread_id':'baseline'}}
    first=graph.invoke({'messages':[{'role':'user','content':'Record the synthetic summary.'}]},cfg)
    pending=interrupts(first)
    assert pending and not effects
    final=graph.invoke(decision(pending),cfg)
    assert len(effects)==1 and not interrupts(final)
    assert json.loads(final['messages'][-1].text)=={'outcome':'baseline_recorded'}
    return {'baseline_passed':True,'pending':pending,'first':plain(first),'final':plain(final),'effects':effects,'trace':trace,'models':[m.trace for m in models]}

def worker(db, phase, pending, gateway, output):
    record={'pid':os.getpid(),'phase':phase,'binding':BINDING,'trace':[]}
    try:
        with SqliteSaver.from_conn_string(db) as saver:
            graph,models=build(saver,lambda args:execute(gateway,args,'resume-execute',record['trace']),record['trace'])
            cfg={'configurable':{'thread_id':'pilot'}}
            if phase=='resume':
                state=graph.get_state(cfg,subgraphs=True)
                record['restored_state']=plain(state)
                record['checkpoint_before']=state.config
                restored=[{'id':i.id,'value':plain(i.value)} for t in state.tasks for i in t.interrupts]
                record['restored_interrupts']=restored
                assert restored==pending,(restored,pending)
                value=decision(pending)
            else: value={'messages':[{'role':'user','content':'Record the synthetic summary.'}]}
            result=graph.invoke(value,cfg)
            state=graph.get_state(cfg,subgraphs=True)
            record.update(result=plain(result),pending=interrupts(result),checkpoint_after=state.config,models=[m.trace for m in models],ok=True)
    except BaseException:
        record.update(ok=False,error=traceback.format_exc())
    output.send(record)

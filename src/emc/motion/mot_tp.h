#ifndef MOT_TP_H //{
#define MOT_TP_H
// motmod -- tpmod interface provisions

//----------------------------------------------------------
// tpmod retrieves motmod function pointers:
extern void emcmot_tp_funcs(void(*DioWrite)(int,char)
                           ,void(*AioWrite)(int,double)
                           ,void(*SetRotaryUnlock)(int,int)
                           ,int( *GetRotaryUnlock)(int)
                           );
extern void(*vector_DioWrite)(int,char);
extern void(*vector_AioWrite)(int,double);
extern void(*vector_SetRotaryUnlock)(int,int);
extern int (*vector_GetRotaryIsUnlocked)(int);

//----------------------------------------------------------
// tpmod retrieves struct pointers:
extern void emcmot_tp_ptrs(emcmot_status_t*
                          ,emcmot_debug_t *
                          ,emcmot_config_t*
                          );

//----------------------------------------------------------
// tpmod supplies tp function pointers: (modular tp)
#define TMOD_EXTERN(fname) \
        extern _##fname mod##fname;

/* Example:
**   TMOD_EXTERN(tpFoo) expands to:
**   extern _tpFoo modtpFoo
*/

TMOD_EXTERN(tpAbort)
TMOD_EXTERN(tpActiveDepth)
TMOD_EXTERN(tpAddCircle)
TMOD_EXTERN(tpAddLine)
TMOD_EXTERN(tpAddRigidTap)
TMOD_EXTERN(tpClear)
TMOD_EXTERN(tpCreate)
TMOD_EXTERN(tpGetExecId)
TMOD_EXTERN(tpGetExecTag)
TMOD_EXTERN(tpGetMotionType)
TMOD_EXTERN(tpGetPos)
TMOD_EXTERN(tpIsDone)
TMOD_EXTERN(tpPause)
TMOD_EXTERN(tpQueueDepth)
TMOD_EXTERN(tpResume)
TMOD_EXTERN(tpRunCycle)
TMOD_EXTERN(tpSetAmax)
TMOD_EXTERN(tpSetAout)
TMOD_EXTERN(tpSetCycleTime)
TMOD_EXTERN(tpSetDout)
TMOD_EXTERN(tpSetId)
TMOD_EXTERN(tpSetPos)
TMOD_EXTERN(tpSetRunDir)
TMOD_EXTERN(tpSetSpindleSync)
TMOD_EXTERN(tpSetTermCond)
TMOD_EXTERN(tpSetVlimit)
TMOD_EXTERN(tpSetVmax)

TMOD_EXTERN(tcqFull)

#undef TMOD_EXTERN
#endif //}

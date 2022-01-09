/********************************************************************
* Description: tp.h
*   Trajectory planner based on TC elements
*
*   Derived from a work by Fred Proctor & Will Shackleford
*
* Author:
* License: GPL Version 2
* System: Linux
*
* Copyright (c) 2004 All rights reserved.
*
********************************************************************/
#ifndef TP_H
#define TP_H

#include "posemath.h"
#include "tc_types.h"
#include "tp_types.h"
#include "tcq.h"

// functions not used by motmod:
int tpAddCurrentPos(TP_STRUCT * const tp, EmcPose const * const disp);
int tpSetCurrentPos(TP_STRUCT * const tp, EmcPose const * const pos);
void tpToggleDIOs(TC_STRUCT * const tc); //gets called when a new tc is taken from the queue. it checks and toggles all needed DIO's
int tpIsMoving(TP_STRUCT const * const tp);
int tpInit(TP_STRUCT * const tp);

// functions used by motmod:
#define TDEF(rtype,fname,fargs) \
    rtype fname fargs; \
    typedef rtype(*_##fname)fargs; \
    extern _##fname v_##fname(void);

/* Example: TDEF(int, tpFoo, (TP_STRUCT * const tp, int bar))
** Expands to make:
**    1)   tpFoo declaration      (legacy compatibility)
**    2)  _tpFoo function typedef (_tpFoo)
**    3) v_tpFoo declaration      (fetch vector address to _tpFoo):
**
**           int   tpFoo (TP_STRUCT * const tp, int bar);
**   typedef int(*_tpFoo)(TP_STRUCT * const tp, int bar);
**   extern _tpFoo v_tpFoo(void);
*/

TDEF(int, tpCreate, (TP_STRUCT * const tp, int _queueSize, TC_STRUCT * const tcSpace))
TDEF(int, tpClear, (TP_STRUCT * const tp))
TDEF(int, tpClearDIOs, (TP_STRUCT * const tp))
TDEF(int, tpSetCycleTime, (TP_STRUCT * tp, double secs))
TDEF(int, tpSetVmax, (TP_STRUCT * tp, double vmax, double ini_maxvel))
TDEF(int, tpSetVlimit, (TP_STRUCT * tp, double limit))
TDEF(int, tpSetAmax, (TP_STRUCT * tp, double amax))
TDEF(int, tpSetId, (TP_STRUCT * tp, int id))
TDEF(int, tpGetExecId, (TP_STRUCT * tp))
TDEF(struct state_tag_t, tpGetExecTag, (TP_STRUCT * const tp))
TDEF(int, tpSetTermCond, (TP_STRUCT * tp, int cond, double tolerance))
TDEF(int, tpSetPos, (TP_STRUCT * tp, EmcPose const * const pos))
TDEF(int, tpRunCycle, (TP_STRUCT * tp, long period))
TDEF(int, tpPause, (TP_STRUCT * tp))
TDEF(int, tpResume, (TP_STRUCT * tp))
TDEF(int, tpAbort, (TP_STRUCT * tp))
TDEF(int, tpAddRigidTap, (TP_STRUCT * const tp,
        EmcPose end,
        double vel,
        double ini_maxvel,
        double acc,
        unsigned char enables,
        double scale,
        struct state_tag_t tag))
TDEF(int, tpAddLine, (TP_STRUCT * const tp, EmcPose end, int canon_motion_type,
	      double vel, double ini_maxvel, double acc, unsigned char enables,
	      char atspeed, int indexrotary, struct state_tag_t tag))
TDEF(int, tpAddCircle, (TP_STRUCT * const tp, EmcPose end, PmCartesian center,
		PmCartesian normal, int turn, int canon_motion_type, double vel,
		double ini_maxvel, double acc, unsigned char enables,
		char atspeed, struct state_tag_t tag))
TDEF(int, tpGetPos, (TP_STRUCT const  * const tp, EmcPose * const pos))
TDEF(int, tpIsDone, (TP_STRUCT * const tp))
TDEF(int, tpQueueDepth, (TP_STRUCT * const tp))
TDEF(int, tpActiveDepth, (TP_STRUCT * const tp))
TDEF(int, tpGetMotionType, (TP_STRUCT * const tp))
TDEF(int, tpSetSpindleSync, (TP_STRUCT * const tp, int spindle, double sync, int wait))

TDEF(int, tpSetAout, (TP_STRUCT * const tp, unsigned char index, double start, double end))
TDEF(int, tpSetDout, (TP_STRUCT * const tp, int index, unsigned char start, unsigned char end)) //gets called to place DIO toggles on the TC queue

TDEF(int, tpSetRunDir, (TP_STRUCT * const tp, tc_direction_t dir))

#undef TDEF
#endif				/* TP_H */

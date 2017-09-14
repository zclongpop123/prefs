#========================================
#    author: Changlong.Zang
#      mail: zclongpop123@163.com
#      time: Thu Sep 14 10:19:32 2017
#========================================
import maya.cmds as mc
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def create_twist_joints(start_jnt, end_jnt, counts=6):
    '''
    '''
    sp = mc.xform(start_jnt, q=True, ws=True, t=True)
    ep = mc.xform(end_jnt,   q=True, ws=True, t=True)

    #- create joints
    twist_joints = list()
    for i in range(counts):
        jnt = mc.createNode('joint')
        #- match positions
        ps = sp[0] + (ep[0] - sp[0]) / (counts-1) * i, sp[1] + (ep[1] - sp[1]) / (counts-1) * i, sp[2] + (ep[2] - sp[2]) / (counts-1) * i
        mc.xform(jnt, ws=True, t=ps)

        #- save to list
        twist_joints.append(jnt)

        #- orient rotation
        mc.delete(mc.orientConstraint(start_jnt, jnt))

        #- parent
        if i:
            mc.parent(jnt, twist_joints[i-1])

    #- freeze attributes
    mc.makeIdentity(twist_joints[0], a=True, r=True)

    return twist_joints





def create_noroll_joints(start_jnt, end_jnt, count=2, near_jnt=None):
    '''
    '''
    noro_joints = create_twist_joints(start_jnt, end_jnt, count)

    for attr in ('tx', 'ty', 'tz'):
        for jnt in noro_joints[1:]:
            mc.setAttr('{0}.{1}'.format(jnt, attr), mc.getAttr('{0}.{1}'.format(jnt, attr)) * 0.1)

    mc.makeIdentity(noro_joints[0], a=True, r=True)
    if near_jnt:
        mc.delete(mc.pointConstraint(near_jnt, noro_joints[0]))

    return noro_joints





def create_aux_joints(end_jnt):
    '''
    '''
    start_jnt = mc.listRelatives(end_jnt, p=True, path=True)
    aux_joints = create_noroll_joints(start_jnt, end_jnt, 3, end_jnt)
    mc.delete(mc.pointConstraint(end_jnt, aux_joints[0]))

    return aux_joints





def create_ik_handle(start_jnt, end_jnt, ik_curve=None):
    '''
    '''
    if not ik_curve:
        ik_curve = mc.curve(d=1, p=[mc.xform(jnt, q=True, ws=True, t=True) for jnt in (start_jnt, end_jnt)])

    result = mc.ikHandle(sj=start_jnt, ee=end_jnt, c=ik_curve, ccv=False, sol='ikSplineSolver')

    return result[0]





def set_ik_advance_twist(ik_handle, world_up_object_start, world_up_object_end):
    '''
    '''
    mc.setAttr('{0}.dtce'.format(ik_handle), 1, l=True)
    mc.setAttr('{0}.dwut'.format(ik_handle), 4, l=True)
    mc.setAttr('{0}.dwua'.format(ik_handle), 3, l=True)
    mc.setAttr('{0}.dwuv'.format(ik_handle), 0, 0, 1, l=True)
    mc.setAttr('{0}.dwve'.format(ik_handle), 0, 0, 1, l=True)
    mc.connectAttr('{0}.wm[0]'.format(world_up_object_start), '{0}.dwum'.format(ik_handle), l=True)
    mc.connectAttr('{0}.wm[0]'.format(world_up_object_end),   '{0}.dwue'.format(ik_handle), l=True)
